/**
 * Created by jz on 5/15/17.
 */
var mongoose = require('mongoose');

var Schema = mongoose.Schema;

// Create a userlike schema.
var userSchema = new Schema({
  email: { type: String},
  zpid: { type: String, required: true },
});



// Map the scehma to database.
var UserLike = mongoose.model('userlikes', userSchema);

module.exports = UserLike;