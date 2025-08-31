// Test file with linting errors
var unused_variable = "This should cause linting errors"
console.log("This should warn")

export const testFunction = () => {
  const unusedVar = "unused"
  return "test"
}