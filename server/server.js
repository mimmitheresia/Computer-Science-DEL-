'use strict';

class LoggedInUsers {
  constructor() {
    this.loggedIn = {};
    this.targetButton = {};
    this.PreviousDescription = {};
  }
  addUser(username) {
    this.loggedIn[username] = true;
  }
  setTarget(username,gender) {
    console.log("Set target: " + username + ":" + gender );
    console.log(gender)
    this.targetButton[username] = gender;
  }
  getTarget(username) {
    console.log("in getTarget:");
    console.log(username);
    console.log(this.targetButton[username])
    if (username in this.targetButton) {
      return this.targetButton[username]
    } else {
      return null;}
  }

  setPreviousDescription(username, classified_des) {
    this.PreviousDescription[username] =classified_des;
  }
  getPreviousDescription(username){
    return this.PreviousDescription[username];
  }
}

const path = require('path'); //  Helps resolve relative paths, into absolute baths, independent of operating system
const express = require('express'); // Express is a very common webserver for Node.js
const db = require('./database');
const users = new LoggedInUsers();

const port = 8989;
const publicPath = path.join(__dirname, 'public');
const app = express();

// Register a custom middleware for logging incoming requests
app.use((req, res, next) => {
  // This is a middleware that logs all incoming requests.
  const t = Date.now();
  next();
  console.log(`[${res.statusCode}] ${req.url} (${Date.now() - t}ms)`);
});
// Register a middleware that adds support for a URL encoded request body.
// This is needed in order to send data to express using a FORM with a POST action.
app.use(express.urlencoded({
  extended: true,
}));

// Serve the login page if a GET request is sent to the root url.
app.get('/', (req, res) => {
  res.sendFile(
    path.join(publicPath, 'login.html'),
  );
  console.log(req.head);
});

app.get("/logo.jpg", function(req, res){
  res.writeHead(200, {'Content-Type': 'image/jpg'});
  res.end("logo.jpg");
})


app.get('/userprofile*', (req, res) => {
  // if sessionid.correctPassword == true:
  //`Welcome ${req.query.user}!`
  res.sendFile(
    path.join(publicPath, 'carpeCompetencia.html'),
  );
  //res.redirect('/?registration= LALALAL' );  
  console.log(req.head)
});

app.get('/signout', (req, res) => {
  res.sendFile(
    path.join(publicPath, 'login.html'),
  );
  console.log(req.head);
});



app.post('/authenticate', (req, res) => {
  db.serialize(() => {
    db.get('SELECT username, password FROM userInfo WHERE username=?', [req.body.username], (err, row) => {
      if (err) {
        throw new Error(err);
      }
      if (row) { // if userid exists
        if (req.body.register) {
          res.redirect('/?registration=not successful. Username already exists.');
        } else if (req.body.login) {
          if (req.body.password === row.password) { // check if password is correct
            users.addUser(row.username)
            res.redirect(`/userprofile?user=${row.username}`);
          } else {
            res.redirect('/?login= not succesful. Password is incorrect');
          }
        }
      } else { // if userid do not exist
        console.log('Row exists');
        if (req.body.register) {
          let usernameContainsDigit = true;
          let usernameContainsLetter;
          let passwordContainsDigit = true;
          let passwordContainsLetter;
          usernameContainsDigit = /\d/.test(req.body.username);
          usernameContainsLetter = /[a-zA-Z]/.test(req.body.username);
          passwordContainsDigit = /\d/.test(req.body.password);
          passwordContainsLetter = /[a-zA-Z]/.test(req.body.password);
          if (!(usernameContainsLetter)) {
            if (req.body.username.toLowerCase().includes('å') || req.body.username.toLowerCase().includes('ä') || req.body.username.toLowerCase().includes('ö')) {
              usernameContainsLetter = true;
            }
          }
          if (!(passwordContainsLetter)) {
            if (req.body.password.toLowerCase().includes('å') || req.body.password.toLowerCase().includes('ä') || req.body.password.toLowerCase().includes('ö')) {
              passwordContainsLetter = true;
            }
          }
          if ((req.body.username.length) < 5) {
            res.redirect('/?registration= not successful. UserID needs to be at least 5 characters');
          } else if ((req.body.password.length) < 5) {
            res.redirect('/?registration= not successful. Password needs to be at least 5 characters');
          } else if (!(passwordContainsDigit) || !(passwordContainsLetter)) {
            res.redirect('/?registration= not successful. Password needs contain at least one letter and one digit');
          } else {
            const statement = db.prepare('INSERT INTO userInfo VALUES (?,?)');
            statement.run(req.body.username, req.body.password);
            statement.finalize();
            res.redirect('/?registration=successful');
          }
        } else if (req.body.login) {
          res.redirect('/?login=not successful. Username does not exist.');
        }
      }
    });
  });
});

app.post('/targetaction*', (req, res) => {
  const username = (req.url).split(":")[1];
  console.log("POST /targetaction")
  console.log(username) 
  if (req.body.target) {
    console.log("Gender:")
    console.log(req.body.target)
    users.setTarget(username,req.body.target);
    res.redirect(`/userprofile/?user=${username}&target=${req.body.target}`) 
  }
});

app.post('/analyzeaction*', (req, res) => {
  console.log("POST /analyzeaction")
  const username = (req.url).split(":")[1];
  console.log(username);
  const target = users.getTarget(username);
  var ongoingGame =  (req.url).split(":")[3];
  console.log("Ongoing game");
  console.log(ongoingGame);
  const des = req.body.hidden;
  if (target){
    if (des) {
      console.log("Description:");
      console.log(des);
      const result = "{[hej] [W] [0.6666666666666666] []} {[på] [W] [0.8137254901960784] []} {[dig] [M] [0.6113744075829385] []} {[vi] [N] [0.5] []} {[söker] [N] [0.5] []} {[en] [M] [0.7536764705882353] []} {[redig,] [M] [1.0] [förträfflig;1.0,ordentlig;0.8344370860927153]} {[stark] [M] [0.6294416243654822] [bärkraftig;1.0,markant;1.0]} {[och] [ ] [0.5] []} {[trevlig] [W] [0.6230339928970066] []} {[kollega] [W] [0.6892551892551892] []} {[genast!] [M] [0.8333333333333333] [omedelbart;1.0,på;0.8137254901960784,med;0.7500000000000001]}"
      if (!ongoingGame) {
        users.setPreviousDescription(result);
      }
      if (ongoingGame){
        
      }
      //const result = "{[Jag] [n] [0.5] []} {[söker] [n] [0.5] []} {[en] [n] [0.5] []} {[redig,] [m] [0.8] [ambitiös,framåt]} {[stark] [m] [0.9] [uthållig]} {[och] [n] [0.5] []} {[vacker] [w] [0.9] []} {[kollega.] [n] [0.5] []}";
      res.redirect(`/userprofile/?user=${username}&target=${target}&analyze= Analyzing...&description=${des}&result=${result}`)
    }
    else {
      res.redirect(`/userprofile/?user=${username}&target=${target}&analyze= Not successful. No text to analyze.`)
    }}
  else {
    res.redirect(`/userprofile/?user=${username}&analyze=Not successful. You have to choose a gender.&description=${des}`)
  }});

app.listen(port, () => {
  console.info(`Listening on port ${port}!`);
});



