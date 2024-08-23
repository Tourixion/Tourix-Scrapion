function checkEmailAndConvertLocalClarityCSV() {
  Logger.log('Script started');
  var threads = GmailApp.search('subject:"LocalClarity - Stavros -Review Download Link" from:reviews@localclarity.com');
  Logger.log('Found ' + threads.length + ' matching email threads');

  // Specify the folder ID where you want to store the spreadsheets
  var folderId = '1feGOt5crxPbY30z61GRQATrKkhSZQGZf'; // Replace with your actual folder ID
  var folder = DriveApp.getFolderById(folderId);

  for (var i = 0; i < threads.length; i++) {
    var messages = threads[i].getMessages();
    Logger.log('Processing thread ' + (i+1) + ' with ' + messages.length + ' messages');

    for (var j = 0; j < messages.length; j++) {
      Logger.log('Processing message ' + (j+1));
      var body = messages[j].getPlainBody();
      var csvLink = extractCSVLink(body);
      
      if (csvLink) {
        Logger.log('Found CSV link: ' + csvLink);
        var csvData = fetchCSVData(csvLink);
        if (csvData) {
          Logger.log('Successfully fetched CSV data');
          try {
            var fileName = 'LocalClarity Stavros Reviews ' + new Date().toISOString().split('T')[0];
            var newSheet = SpreadsheetApp.create(fileName);
            var sheet = newSheet.getActiveSheet();
            
            var csvArray = Utilities.parseCsv(csvData);
            sheet.getRange(1, 1, csvArray.length, csvArray[0].length).setValues(csvArray);
            
            // Move the created spreadsheet to the specified folder
            var file = DriveApp.getFileById(newSheet.getId());
            folder.addFile(file);
            DriveApp.getRootFolder().removeFile(file);
            
            Logger.log('Created new sheet in specified folder: ' + newSheet.getUrl());
            messages[j].star();
            Logger.log('Marked email as processed');
          } catch (e) {
            Logger.log('Error creating sheet: ' + e.toString());
          }
        } else {
          Logger.log('Failed to fetch CSV data');
        }
      } else {
        Logger.log('No CSV link found in this message');
      }
    }
  }
  Logger.log('Script completed');
}

function extractCSVLink(body) {
  var linkRegex = /(https:\/\/reputation-manager\.s3.*?\.csv)/i;
  var match = body.match(linkRegex);
  return match ? match[1] : null;
}

function fetchCSVData(url) {
  try {
    var response = UrlFetchApp.fetch(url);
    if (response.getResponseCode() == 200) {
      return response.getContentText();
    } else {
      Logger.log('HTTP error: ' + response.getResponseCode());
    }
  } catch (e) {
    Logger.log('Error fetching CSV: ' + e.toString());
  }
  return null;
}
