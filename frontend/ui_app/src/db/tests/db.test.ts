import database from "../Database";
import "fake-indexeddb/auto";

/**
 * Chaining Database functions with callbacks to test get and set
 * "fake-indexeddb/auto" required to run test under node environment
 */
test('we can set and get from database', (done) => {
    let db = database;
    db.setBulkItem('test', { username: 'user1' }, () => {
        db.getBulkItem('test', (data: any) => {
            expect(data.username).toBe("user1");
            done();
        });
    });
});
