var express = require('express');
var passwordHash = require('password-hash');
var session = require('client-sessions');
var User = require('../model/user');
var rpc_client = require('../rpc_client/rpc_client');
var router = express.Router();
var Geohash = require('latlon-geohash');
var NodeGeocoder = require('node-geocoder');

//google geocoder api initialization
var options = {
  provider: 'google',

  // Optional depending on the providers
  httpAdapter: 'https', // Default
  apiKey: 'AIzaSyDpZGZWXqyRWeBvLjmMf5LxC3kvGE7nXMc', // for Mapquest, OpenCage, Google Premier
  formatter: null         // 'gpx', 'string', ...
};
var geocoder = NodeGeocoder(options);
TITLE = 'capstone';

/* Index page */
router.get('/', function(req, res, next) {
  var user = checkLoggedIn(req, res)
  res.render('index', { title: TITLE, logged_in_user: user });
});
/*testing estimation*/
router.get('/estimator', function(req, res, next) {

  res.render('estimator', { title: TITLE });
});

router.get('/estimation_summary', function(req, res, next) {


  geocoder.geocode(req.query.address, function(err, resp) {
    var gh = Geohash.encode(resp[0].latitude,resp[0].longitude, [5]);
    var query = {
        "address" : req.query.address,
        "ptype" : req.query.ptype,
        "geohash" : gh,
        "floor_size" : req.query.floor_size,
        "lot_size" : req.query.lot_size,
        "bedr" : req.query.bedr,
        "bathr" : req.query.bathr,
        "es" : req.query.es,
        "ms" : req.query.ms,
        "hs" : req.query.hs,
        "new_floor_size" : req.query.new_floor_size,
        "new_lot_size" : req.query.new_lot_size,
        "new_bedr" : req.query.new_bedr,
        "new_bathr" : req.query.new_bathr,
        "new_es" : req.query.new_es,
        "new_ms" : req.query.new_ms,
        "new_hs" : req.query.new_hs
        }
    console.log(query)
    rpc_client.getEstimation(query, function(response) {

            console.log("inside rpc : " + query.geohash)
            console.log("rpc working")
            console.log(response)

    });
    res.render('estimation_summary', {
        title: TITLE,
        address: query.address,
        ptype: query.ptype,
        geohash : query.geohash,
        floor_size : query.floor_size,
        lot_size : query.lot_size,
        bedr : query.bedr,
        bathr : query.bathr,
        es : query.es,
        ms : query.ms,
        hs : query.hs,
        new_floor_size : query.new_floor_size,
        new_lot_size : query.new_lot_size,
        new_bedr : query.new_bedr,
        new_bathr : query.new_bathr,
        new_es : query.new_es,
        new_ms : query.new_ms,
        new_hs : query.new_hs
         });
  });


});

/* Search page */
router.get('/search', function(req, res, next) {
  var query = req.query.search_text;
  console.log("search text: " + query)

  rpc_client.searchArea(query, function(response) {
    results = [];
    if (response == undefined || response === null) {
      console.log("No results found");
    } else {
      results = response;
    }

    // Add thousands separators for numbers.
    addThousandSeparatorForSearchResult(results)

    res.render('search_result', {
      title: TITLE,
      query: query,
      results: results
    });

  });
});

/* Property detail page*/
router.get('/detail', function(req, res, next) {
  logged_in_user = checkLoggedIn(req, res)

  var id = req.query.id
  console.log("detail for id: " + id)

  rpc_client.getDetailsByZpid(id, function(response) {
    property = {}
    if (response === undefined || response === null) {
      console.log("No results found");
    } else {
      property = response;
    }

    // Handle predicted value
    var predicted_value = parseInt(property['predicted_value']);
    var list_price = parseInt(property['list_price']);
    property['predicted_change'] = ((predicted_value - list_price) / list_price * 100).toFixed(2);

    // Add thousands separators for numbers.
    addThousandSeparator(property);

    // Split facts and additional facts
    splitFacts(property, 'facts');
    splitFacts(property, 'additional_facts');


    res.render('detail', 
      {
        title: 'Smart Zillow',
        query: '',
        logged_in_user: logged_in_user,
        property : property
      });
  });
});

/* Login page */
router.get('/login', function(req, res, next) {
  res.render('login', { title: TITLE });
});

/* Login submit */
router.post('/login', function(req, res, next) {
  var email = req.body.email;
  var password = req.body.password;

  User.find({ email : email }, function(err, users) {
    console.log(users);
    if (err) throw err;
    // User not found.
    if (users.length == 0) {
      res.render('login', {
        title : TITLE,
        message : "User not found. Or <a href='/register'>rigester</a>"
      });
    } else {
      // User found.
      var user = users[0];
      if (passwordHash.verify(password, user.password)) {
        req.session.user = user.email;
        res.redirect('/');
      } else {
        res.render('login', {
          title : TITLE,
          message : "Password incorrect. Or <a href='/register'>rigester</a>"
        });
      }
    }
  });
});

/* Register page */
router.get('/register', function(req, res, next) {
  res.render('register', { title: TITLE });
});

/* Register submit */
router.post('/register', function(req, res, next) {
  // Get form values.
  var email = req.body.email;
  var password = req.body.password;
  var hashedPassword = passwordHash.generate(password);

  // Check if the email is already used.
  User.find({ email : email }, function(err, users) {
    if (err) throw err;
    if (users.length > 0) {
      console.log("User found for: " + email);
      res.render('register', {
        title: TITLE,
        message: 'Email is already used. Please pick a new one. Or <a href="/login">Login</a>'
      });
    } else {
        var newUser = User({
          email : email,
          password : hashedPassword,
        });
        // Save the user.
        newUser.save(function(err) {
          if (err) throw err;
          console.log('User created!');
          req.session.user = email;
          res.redirect('/');
        });
    }
  });
});

/* Logout */
router.get('/logout', function(req, res) {
  req.session.reset();
  res.redirect('/');
});


function checkLoggedIn(req, res) {
  // Check if session exist
  if (req.session && req.session.user) { 
    return req.session.user;
  }
  return null;
}

function splitFacts(property, field_name) {
  facts_groups = [];
  group_size = property[field_name].length / 3;
  facts_groups.push(property[field_name].slice(0, group_size));
  facts_groups.push(property[field_name].slice(group_size, group_size + group_size));
  facts_groups.push(property[field_name].slice(group_size + group_size));
  property[field_name] = facts_groups;
}

function addThousandSeparatorForSearchResult(searchResult) {
  for (i = 0; i < searchResult.length; i++) {
    addThousandSeparator(searchResult[i]);
  }
}

function addThousandSeparator(property) {
  property['list_price'] = numberWithCommas(property['list_price']);
  property['size'] = numberWithCommas(property['size']);
  property['predicted_value'] = numberWithCommas(property['predicted_value']);
}

function numberWithCommas(x) {
  if (x != null) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
}

//function addressToGeohash(address){
//    geocoder.geocode(address, function(err, res) {
//    var gh = Geohash.encode(res[0].latitude,res[0].longitude, [5]);
//    console.log("inside: " + gh);
//    return gh
//
//  });


module.exports = router;
