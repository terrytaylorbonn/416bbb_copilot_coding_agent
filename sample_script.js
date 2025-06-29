// Sample JavaScript - Created for Code Review Agent Testing
// This file intentionally contains issues for review testing

var globalVar = "should use let or const";  // Should flag var usage
var anotherVar = "more var usage";

function testFunction() {
    console.log("Debug message 1");  // Should flag console.log
    console.log("Debug message 2");  // Another console.log
    
    var localVar = "local variable";  // More var usage
    console.log("Local var:", localVar);  // More console.log
    
    return "test complete";
}

// Call the function
testFunction();
console.log("Script finished");  // Final console.log
