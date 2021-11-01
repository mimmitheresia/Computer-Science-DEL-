'use strict';

class LoggedInUsers {
  constructor() {
    this.loggedIn = {};
    this.targetButton = {};
  }
  addUser(username) {
    this.loggedIn[username] = true;
  }
  setTarget(username,gender) {
    console.log("in set target:");
    console.log(gender)
    this.targetButton[username] = gender;
    console.log(JSON.stringify(this.targetButton));
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
}

class PythonData {
  constructor() {
    this.probabilities = {};
    this.synonyms = {};
  }
}

var python_data = new PythonData();

const path = require('path'); //  Helps resolve relative paths, into absolute baths, independent of operating system
const express = require('express'); // Express is a very common webserver for Node.js
const db = require('./database');
const { performance } = require('perf_hooks');
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
          } else if (!(usernameContainsDigit) || !(usernameContainsLetter)) {
            res.redirect('/?registration= not successful. UserID needs to contain at least one letter and one digit');
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
  //const spawn = require("child_process").spawn;
  console.log(username);
  const target = users.getTarget(username);
  const des = req.body.hidden;
  if (target){
    if (des) {
      const exec = require("child_process").execSync;
      var resu = exec(`python3 /Users/ewelynstrandberg/Desktop/KTH/DEL/DEL/analyzeInput.py ${des}`);
      console.log(resu.toString("utf8"));
      const prel_result = resu.toString("utf8");
      const no_vinge = prel_result.substring(3,prel_result.length-1);
      const word_lemma_pairs = no_vinge.split("|");
    
      var output = "";
      var gender
      for (let index in word_lemma_pairs){
        const split_word_and_lemma = word_lemma_pairs[index].split(" ");
        const word = split_word_and_lemma[0];
        const lemma = split_word_and_lemma[1];
        var prob = python_data.probabilities[lemma];
       
        if (typeof prob == 'undefined'){
          gender = "u"
          prob = "u"
        }
        else if (prob > 0.65){
          gender = "w";
        } else if (prob < 0.35){
          gender = "m";
        }else{
          gender = "n";
        }
        output += "{[" + word + "] [" + gender + "] [" + prob.toString() + "] [";

        const synonyms = python_data.synonyms[lemma]
        var formatted_synonyms = "";
        if (gender != "u"){
          for (let index2 in Object.keys(synonyms)){
            const synonym = Object.keys(synonyms)[index2];
            const value = python_data.synonyms[lemma][synonym];
            formatted_synonyms += synonym + ";" + value.toString() + ",";
          }
        }  
        const synonyms_str = formatted_synonyms.substring(0,formatted_synonyms.length-1) + "]}";
        output += synonyms_str;
      }
      output += "}";
      console.log(output);

      res.redirect(`/userprofile/?user=${username}&target=${target}&analyze= Analyzing...&description=${des}&result=${output}`)
      
    }
    else {
      res.redirect(`/userprofile/?user=${username}&target=${target}&analyze= Not successful. No text to analyze.`)
    }}
  else {
    res.redirect(`/userprofile/?user=${username}&analyze=Not successful. You have to choose a gender.&description=${des}`)
  }});

function handleFiles() {
    var startTime = performance.now()
    const readLine = require('readline');
    const f = require('fs');
    var file = '/Users/ewelynstrandberg/Desktop/KTH/DEL/DEL/All_information.txt';
    var rl = readLine.createInterface({
        input : f.createReadStream(file),
        output : process.stdout,
        terminal: false
    });
    rl.on('line', function (text) {
      const lemma = text.split("[")[0].substring(1,text.split("[")[0].length)
      const leftover_line = text.split("[")[1]
      const end_of_prob_index = leftover_line.indexOf(",");
      const lemma_probability = leftover_line.substring(0,end_of_prob_index);
      python_data.probabilities[lemma] = parseFloat(lemma_probability);
      const synonym_start = leftover_line.indexOf("{");
      if (leftover_line.charAt(synonym_start+2)!="}") {
        const merge_syns_and_probs = leftover_line.substring(synonym_start+1,leftover_line.length-3);
        const syns_and_probs = merge_syns_and_probs.split(",");
        var syndict = {};
        for (let index in syns_and_probs) {
          const split_syn_and_prob = syns_and_probs[index].split(":");
          const syn = split_syn_and_prob[0];
          const prob = parseFloat(split_syn_and_prob[1]);
          syndict[syn] = prob;
  
        }
        python_data.synonyms[lemma] = syndict;
      } else {
        python_data.synonyms[lemma] = {};
      }
    }).on("close", function() {
      var endTime = performance.now()
      console.log(`End of file, it took ${(endTime - startTime)/1000} seconds to complete`);
    });
  }

app.listen(port, () => {
  handleFiles();
  console.info(`Listening on port ${port}!`);
});
