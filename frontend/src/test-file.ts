// Test file with linting errors
var unused_variable = "This should cause linting errors"
console.log("This should warn")
let another_var = "more errors"

export const testFunction = () => {
  const unusedVar = "unused"
  return "test"
}