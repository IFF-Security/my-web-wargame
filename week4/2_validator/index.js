var assert = require("assert");
var validator = require('validator');

assert(validator.isDate("2025-07-25"));
assert(validator.isEmail("runas8128@hanyang.ac.kr"));
assert(validator.isJSON('{ "status": 200, "text": "ok" }'));
assert(validator.isNumeric("3.14159265358979"));
assert(validator.isPort("8080"));
console.log("All test passed!");
