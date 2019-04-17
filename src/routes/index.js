var express = require('express');
var router = express.Router();
var path = require('path');
var childProcess = require('child_process');
var exec = require('child_process').exec;
var fs = require('fs');

/* GET home page. */
router.get('/', function(req, res, next) 
{
  //req.body.username
  //res.render('index', { title: 'Express' });
  //res.send("Hello");
  res.sendFile(path.join(__dirname, '../', 'index.html'));
  
});

router.post('/my_aptrace', function(req, res, next) {
  var spec_data = req.body['spec_data_3sf'],
    spec_width = req.body['spec_width'],
    new_spec_height = req.body['new_spec_height'],
    tempfile_name = req.body['tempfile_name'];
  console.log(new_spec_height);
  console.log(path.join(__dirname, "..", 'public', tempfile_name));
  fs.writeFile(
    path.join(__dirname, "..", 'public', tempfile_name),
    spec_data, (err) => {
      if (err) throw err;
      console.log('The file has been saved!');

      let result = '';
      let command = 'python3 ' + path.join(__dirname, '..', 'public', 'apIdentify.py') + ' ' +
        path.join(__dirname, "..", 'public', tempfile_name) + ' ' +
        spec_width + ' ' + new_spec_height;
      console.log(command);
      let pythonProcess = exec(command);

      //console.log(pythonProcess);
      pythonProcess.stdout.on('data', function(data) {
      // Do something with the data returned from python script
        //console.log(data);
        result += data;
      });

      pythonProcess.stdout.on('end', function() {
      // Do something with the data returned from python script
        result = JSON.parse(result);
      });

      pythonProcess.on('exit', function (code, signal) {
        console.log('child process exited with ' +
                    `code ${code} and signal ${signal}`);
        //console.log(result);
        res.send(result);
      });
    }
  );
});

module.exports = router;
