// Small logic checks using Node's standard library. Real DOM rendering is
// verified separately in the browser; this stub deliberately does not parse HTML.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const elements = new Map();
const element = id => {
    if (!elements.has(id)) elements.set(id, {
        value: '', textContent: '', innerHTML: '', className: '', disabled: false,
        replaceChildren() { this.innerHTML = ''; },
    });
    return elements.get(id);
};
const context = vm.createContext({
    document: { getElementById: element, createElement: () => ({ textContent: '', innerHTML: '' }) },
    fetch: async () => { throw new Error('unexpected request'); },
});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../frontend/index.js'), 'utf8'), context);
const run = code => vm.runInContext(code, context);

(async () => {
    context.fetch = async () => ({ ok: true, status: 200, json: async () => ({ status: 'success' }) });
    assert.equal((await run('callApi("/movies")')).status, 'success');
    context.fetch = async () => ({ ok: false, status: 422, json: async () => ({ detail: [{ loc: ['body', 'title'], msg: 'required' }] }) });
    await assert.rejects(run('callApi("/movies")'), /HTTP 422: body.title: required/);
    context.fetch = async () => ({ ok: false, status: 500, json: async () => { throw new Error('not JSON'); } });
    await assert.rejects(run('callApi("/movies")'), /HTTP 500/);
    context.fetch = async () => { throw new Error('offline'); };
    await assert.rejects(run('callApi("/movies")'), /Cannot reach the API/);

    element('add-title').value = 'Keep this title';
    element('add-genres').value = 'Drama';
    await run('addMovie()');
    assert.equal(element('add-feedback').className, 'error');
    assert.equal(element('add-title').value, 'Keep this title');
    assert.equal(element('add-button').disabled, false);

    let calls = 0;
    context.fetch = async () => { calls++; throw new Error('should not be used'); };
    run('searchedMovies = {1: {title: "Toy Story"}, 32: {title: "Twelve Monkeys"}}');
    run('rateMovie(1, "5"); rateMovie(32, "2")');
    assert.equal(run('myRatings[1].rating'), 5);
    assert.equal(element('ratings-count').textContent, 2);
    assert.equal(calls, 0, 'local ratings must not hit an endpoint');
    run('rateMovie(1, "5.5")');
    assert.equal(run('myRatings[1].rating'), 5);
    assert.match(run('ratingDropdown(1)'), /value='5' selected/);

    let finish;
    context.fetch = async (_url, options) => {
        assert.deepEqual(JSON.parse(options.body), {ratings: [{movieId: 1, rating: 5}, {movieId: 32, rating: 2}]});
        return new Promise(resolve => { finish = resolve; });
    };
    const pending = run('getRecommendations()');
    assert.equal(element('rec-button').disabled, true);
    run('removeRating(32)');
    finish({ ok: true, status: 200, json: async () => ({recommendations: [{movieId: 3, title: 'stale', genres: 'Drama', predictedRating: 4}]}) });
    await pending;
    assert.equal(element('rec-results').innerHTML, '', 'discard response for old ratings');
    assert.equal(element('rec-button').disabled, false);
    assert.match(element('rec-feedback').textContent, /Ratings changed/);
    await run('getRecommendations()');
    assert.match(element('rec-feedback').textContent, /at least two movies/);
    console.log('Frontend checks passed: HTTP errors, preserved input, local ratings, validation, stale response, guidance.');
})().catch(error => { console.error(error); process.exitCode = 1; });
