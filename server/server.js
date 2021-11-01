'use strict';

class PythonData {
  constructor() {
    this.probabilities = {};
    this.synonyms = {};
  }
}

class LoggedInUsers {
  constructor(username) {
    this.loggedIn = {};}

  addUser(username, userObject) {
    this.loggedIn[username] = userObject;}
  getUserObject(username){
    return this.loggedIn[username];}}

class UserObject {
  constructor(username) {
    this.username;
    this.targetButton;
    this.old_term_to_syntax = {};
    this.new_term_to_syntax = {};
    this.is_it_Unclassified_Term = [];}
 
  resetPreviousTable(){
    this.old_term_to_syntax = {};
    this.new_term_to_syntax = {};
    this.is_it_Unclassified_Term = [];
  }  
  setTarget(gender) {
    this.targetButton = gender;}

  getTarget() {
      return this.targetButton;} 
    
  getpreviousClassified_Description(){
    return this.previousClassified_Description;}

  isClassifiedBefore(term){
    if (term in this.old_term_to_syntax)
    {return true;}
    else {return false;}}}

/* -----------  START APP EXPRESS ------------------------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- */

const path = require('path'); //  Helps resolve relative paths, into absolute baths, independent of operating system
const express = require('express'); // Express is a very common webserver for Node.js
const db = require('./database');
const loggedIn = new LoggedInUsers();
const port = 8989;
const publicPath = path.join(__dirname, 'public');
const app = express();
const python_data = new PythonData();
const { performance } = require('perf_hooks');

    
app.use((req, res, next) => {const t = Date.now();next();console.log(`[${res.statusCode}] ${req.url} (${Date.now() - t}ms)`);});
app.use(express.urlencoded({extended: true,}));
app.get('/', (req, res) => {res.sendFile(path.join(publicPath, 'login.html'),);console.log(req.head);});
app.get('/userprofile*', (req, res) => {res.sendFile(path.join(publicPath, 'carpeCompetencia.html'),);console.log(req.head)});
app.get('/signout', (req, res) => {res.sendFile(path.join(publicPath, 'login.html'),);console.log(req.head);});


app.post('/authenticate', (req, res) => {
  db.serialize(() => {
    db.get('SELECT username, password FROM userInfo WHERE username=?', [req.body.username], (err, row) => {
      if (err) {throw new Error(err);}
      if (row) { // if userid exists
        if (req.body.register) {
          res.redirect('/?registration=not successful. Username already exists.');} 
        else if (req.body.login) {
          if (req.body.password === row.password) { // check if password is correct
            var userObject= new UserObject(row.username);
            loggedIn.addUser(row.username, userObject)
            res.redirect(`/userprofile?user=${row.username}`);} 
          else {
            res.redirect('/?login= not succesful. Password is incorrect');}}} 
        
        if (!row){ // if userid do not exist   
          if (req.body.register) {
            let usernameContainsLetter;
            let passwordContainsLetter;
            usernameContainsLetter = /[a-zA-Z]/.test(req.body.username);
            passwordContainsLetter = /[a-zA-Z]/.test(req.body.password);
            if (!(usernameContainsLetter)) {
              if (req.body.username.toLowerCase().includes('å') || req.body.username.toLowerCase().includes('ä') || req.body.username.toLowerCase().includes('ö')) {usernameContainsLetter = true;}}

            if (!(passwordContainsLetter)) {
              if (req.body.password.toLowerCase().includes('å') || req.body.password.toLowerCase().includes('ä') || req.body.password.toLowerCase().includes('ö')) {passwordContainsLetter = true;}}

            if ((req.body.username.length) < 5) {
              res.redirect('/?registration= not successful. UserID needs to be at least 5 characters');} 
            else if ((req.body.password.length) < 5) {
              res.redirect('/?registration= not successful. Password needs to be at least 5 characters');} 
          
            else {
              const statement = db.prepare('INSERT INTO userInfo VALUES (?,?)');
              statement.run(req.body.username, req.body.password);
              statement.finalize();
              res.redirect('/?registration=successful');}} 
            else if (req.body.login) {res.redirect('/?login=not successful. Username does not exist.');}}});});
});

app.post('/targetaction*', (req, res) => {
  var uO;
  var username = (req.url).split(":")[1];
  var target;
  console.log("POST /targetaction")
  if (req.body.target) {
    target = req.body.target;
    console.log("Target choise: " + target);

    if (username in loggedIn.loggedIn){
      uO = loggedIn.getUserObject(username);} else { uO = new UserObject(username);loggedIn.addUser(username, uO); }// USER IS 

    uO.setTarget(req.body.target);    
    res.redirect(`/userprofile/?user=${username}&target=${req.body.target}`)}
});

app.post('/analyzeaction*', (req, res) => {
  var uO;
  var username = (req.url).split(":")[1];
  var target;
  var description;
  var ongoingGame;
  var result;
  if (username in loggedIn.loggedIn){
    uO = loggedIn.getUserObject(username);} 
  
  else {
    target = (req.url).split(":")[2];
    console.log("target in else:" + target);
    uO = new UserObject(username);
    loggedIn.addUser(username, uO); }// USER IS ALREADY IN 
  
  target = uO.getTarget();  
  description = req.body.hidden;
  ongoingGame =  (req.url).split(":")[3];
  console.log("Username: " + username + ": Target: " + target);
  console.log("Description: " + description);
  console.log("OngoingGame : " + ongoingGame);
  if (target){

    if (description) {
      if (ongoingGame === "false") {
        ongoingGame = false;     
        result = classify(description);  
        set_Old_Term_to_Syntax(uO,result);
        console.log("Term to syntax: ");
        console.log(" ");
        for (var u in uO.old_term_to_syntax){
          console.log(u + ":" + uO.old_term_to_syntax[u]);}
          res.redirect(`/userprofile/?user=${username}&target=${target}&ongoingGame=${ongoingGame}&analyze= Analyzing...&description=${description}&result=${result}`)}
          
      if (ongoingGame === "true") {
        console.log(req.url);
        var carpe_score = (req.url).split(":")[4];
        var first_nr_exkluding_words =  (req.url).split(":")[5];
        var nr_exkluding_words =  (req.url).split(":")[6];
        var exkluding_words_before =  (req.url).split(":")[7];
        var nr_attractive_words =  (req.url).split(":")[8];
        var nr_changed_words  =  (req.url).split(":")[9];
        var changing_words_before =  (req.url).split(":")[10];
        var nr_of_words =  (req.url).split(":")[11];
        ongoingGame = true;

        var unclassified_description = extract_Unclassified_Terms(uO, description);
        console.log("Unclassified description: ");
        console.log(unclassified_description);
        var result_of_new_terms = classify(unclassified_description,ongoingGame);

        set_New_Term_Syntax(uO,result_of_new_terms);
        result = mergeResultOfOld_New_Terms(uO,result_of_new_terms);
        uO.resetPreviousTable();
        set_Old_Term_to_Syntax(uO,result);
      
        res.redirect(`/userprofile/?user=${username}&target=${target}&ongoingGame=${ongoingGame}&analyze= Analyzing...&description=${description}&result=${result}&carpe_score=${carpe_score}&first_nr_exkluding_words=${first_nr_exkluding_words}&nr_exkluding_words=${nr_exkluding_words}&exkluding_words_before=${exkluding_words_before}&nr_attractive_words=${nr_attractive_words}&nr_changed_words=${nr_changed_words}&changing_words_before=${changing_words_before}&nr_of_wordse=${nr_of_words} `)}
     
    }

    
      if (!description) {
      res.redirect(`/userprofile/?user=${username}&target=${target}&analyze= Not successful. No text to analyze.`)}}

  if (!target) {
    res.redirect(`/userprofile/?user=${username}&analyze=Not successful. You have to choose a gender.&description=${description}`)
  }});


  /*  FUNCTIONS ---------------------------------------------------------------------------------------------------- */
  /* ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ */

  function set_Old_Term_to_Syntax(uO,result){ 
    var result_by_word = result.split("{").slice(1);
    for (var i in result_by_word) { 
      var has_syn = false;  
      var word_result = result_by_word[i].replace("}","");
      var word_res = word_result.split("[");
      var word = word_res[1].replace("]","").trim();
      var synonyms =  word_res[4].replace("]","").trim(); // 
      synonyms = synonyms.split(",");
      
      //Check if last char of word is a comma or punctation (Add tagNodes without underlines for those characters.)
      var last_char = word.charAt(word.length-1);
      var wordContainsChar = /[,.!]/.test(last_char);
      if (wordContainsChar){ var clean_term = word.substring(0, word.length-1);}
      else {var clean_term = word;}
      
      uO.old_term_to_syntax[clean_term.toLowerCase()] =  "{"+ word_result +"} ";
  
      if (synonyms.length === 1) {var is_it_syn = synonyms[0];
        if (is_it_syn === ""){has_syn = false;}
        else {has_syn = true;}}
      if (synonyms.length > 1) {has_syn = true;}
  
      if (has_syn){
        for (var t in synonyms){
          var syn_object = synonyms[t].split(";");
          var syn = syn_object[0].replace("]","");
          uO.old_term_to_syntax[syn.toLowerCase()] = false;}}}}

function extract_Unclassified_Terms(uO, description){
    var unclassified_description = "";
    var description_by_word = description.trim(/[\s]/).split(/[\s]/);
    console.log("Description split by space: " + description_by_word);
    
    for (var i in description_by_word){
      var word = description_by_word[i];
      var last_char = word.charAt(word.length-1);
      var wordContainsChar = /[,.!]/.test(last_char);
      if (wordContainsChar){ 
        var clean_term = word.substring(0, word.length-1).trim(/[\s]/);}
      else {
        var clean_term = word.trim(/[\s]/);}

      if (!(clean_term.toLowerCase() in uO.old_term_to_syntax)){
        console.log("Clean term is new: " + clean_term);
        unclassified_description += clean_term + " ";   
        uO.is_it_Unclassified_Term.push(clean_term.toLowerCase());
        uO.is_it_Unclassified_Term.push(true);}    
        
      if (clean_term.toLowerCase() in uO.old_term_to_syntax){
          console.log("Clean term is old: " + clean_term);
          uO.is_it_Unclassified_Term.push(clean_term.toLowerCase());
          uO.is_it_Unclassified_Term.push(false);}}
    
    return unclassified_description;}

function set_New_Term_Syntax(uO,result_of_new_terms){
  var result_by_word = result_of_new_terms.split("{").slice(1);
  for (var i in result_by_word) { 
    var word_result = result_by_word[i].replace("}","");
    var word_res = word_result.split("[");
    var word = word_res[1].replace("]","").trim();
    
    //Check if last char of word is a comma or punctation (Add tagNodes without underlines for those characters.)
    var last_char = word.charAt(word.length-1);
    var wordContainsChar = /[,.!]/.test(last_char);
    if (wordContainsChar){ var clean_term = word.substring(0, word.length-1);}
    else {var clean_term = word;}  
    console.log(clean_term + ": " + word_result);
    uO.new_term_to_syntax[clean_term.toLowerCase()] =  "{ " + word_result + " } ";}}


function mergeResultOfOld_New_Terms(uO){
  var merged_result = "";
  for (var u=0; u < uO.is_it_Unclassified_Term.length; u++) {
      var clean_lower_term = uO.is_it_Unclassified_Term[u];
      console.log("clean lower term: " + clean_lower_term);
      if (uO.is_it_Unclassified_Term[u+1]){
        console.log("NEW: " + clean_lower_term +  ": " + uO.new_term_to_syntax[clean_lower_term]);
        merged_result += uO.new_term_to_syntax[clean_lower_term];}
      if (!uO.is_it_Unclassified_Term[u+1]){ 
        console.log("OLD: " + clean_lower_term +  ": " + uO.old_term_to_syntax[clean_lower_term]);
        merged_result += uO.old_term_to_syntax[clean_lower_term];}
  u+=1;}
  return merged_result;}


function classify(des, ongoingGame){
    
  var exec = require("child_process").execSync;
  var resu = exec(`python3 /Users/ewelynstrandberg/Desktop/KTH/DEL/DEL/analyzeInput.py ${des}`);
  console.log(resu.toString("utf8"));
  var prel_result = resu.toString("utf8");
  var no_vinge = prel_result.substring(3,prel_result.length-1);
  var word_lemma_pairs = no_vinge.split("|");

  var result = "";
  var gender
  for (let index in word_lemma_pairs){
    var split_word_and_lemma = word_lemma_pairs[index].split(" ");
    var word = split_word_and_lemma[0];
    var lemma = split_word_and_lemma[1];
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
    result += "{[" + word + "] [" + gender + "] [" + prob.toString() + "] [";

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
    result += synonyms_str;
  }
  result += "}";
  console.log(result);
    return result;}


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


