// Configuration: Map locations to their respective spreadsheet IDs and sheets
const LOCATION_MAPPING = {
 'ΔΑΕΑΝ': {
    spreadsheetId: '117DT0fUjExQCfCxgxclF61cj0N9lDnjZMtu-gSHeAB4',
    venues: {
      'Almiros': {
        address: 'P.E.O. Irakliou-Agiou Nikolaou 721 00, Greece', 
        sheets: {
          'tripadvisor': '2024 Tripadvisor Almiros'
        }
      },
       'Voulisma': {
        address: 'Ethniki Odos Agiou Nikolaou Sitias, Istron 721 00, Greece', 
        sheets: {
          'tripadvisor': '2024 Tripadvisor Voulisma Beach'
        }
      },
        'Elounda': {
        address: 'Epar.Od. Agiou Nikolaou - Vrouchas 45, Elounda, Crete 720 53 Greece', 
        sheets: {
          'tripadvisor': '2024 Tripadvisor Elounda Beach'
        }
      },
      // Add more venues as needed
    }
    
  },
  'Hotel Papas': {
    spreadsheetId: '1CJ2O-ZZxfqFsB4TANK71Pgz1DQRQqT309JGBOwpMh8g',
    venues: {
      'Hotel Papas Booking Index': {
        address: 'Πεζούλια - Πευκάκι, Λουτράκι, 20300, Ελλάδα', 
        sheets: {
          'Booking Index': 'Booking 2024'
        }
      },
      'Hotel Papas Google': {
        address: 'Pezoulia Pefkaki Loutraki', 
        sheets: {
          'google': 'Google 2024'
        }
      },
      'Hotel Papas Tripadvisor': {
        address: 'Pezoulia Pefkaki 203 00, Ελλάδα', 
        sheets: {
          'tripadvisor': 'Tripadvisor 2024'
        }
      },
      // Add more venues as needed
    }
    
  },

  
  // Add more locations if needed
};

//

// Folder ID where the weekly files are stored
const SOURCE_FOLDER_ID = '1feGOt5crxPbY30z61GRQATrKkhSZQGZf'; // Replace with the actual folder ID

// File name pattern to match
const FILE_NAME_PATTERN = /^LocalClarity Stavros Reviews \d{4}-\d{2}-\d{2}$/;

// Target structure
const TARGET_COLUMNS = ['reviewId', 'author', 'authorUrl', 'reviewTitle', 'reviewBody', 'language', 'reviewRating', 'dateCreated', 'translation', 'reply'];

function findMostRecentSourceFile() {
  var folder = DriveApp.getFolderById(SOURCE_FOLDER_ID);
  var files = folder.getFiles();
  var latestFile = null;
  var latestDate = null;

  while (files.hasNext()) {
    var file = files.next();
    var fileName = file.getName();
    if (FILE_NAME_PATTERN.test(fileName)) {
      var fileDateStr = fileName.split(' ').pop(); // Get the date part
      var fileDate = new Date(fileDateStr);
      if (latestDate === null || fileDate > latestDate) {
        latestFile = file;
        latestDate = fileDate;
      }
    }
  }

  if (latestFile === null) {
    throw new Error('No matching file found in the specified folder.');
  }

  Logger.log('Found latest file: ' + latestFile.getName() + ' (Date in filename: ' + latestDate.toISOString().split('T')[0] + ')');
  return latestFile;
}

function transferData() {
  Logger.log('Starting data transfer');
  
  var email = Session.getActiveUser().getEmail();
  Logger.log("Script running as: " + email);

  try {
    var sourceFile = findMostRecentSourceFile();
    var sourceSpreadsheet = SpreadsheetApp.open(sourceFile);
    Logger.log('Successfully opened source spreadsheet: ' + sourceSpreadsheet.getName());
  } catch (e) {
    Logger.log('Error opening source spreadsheet: ' + e.toString());
    return;
  }
  
  var sourceSheet = sourceSpreadsheet.getSheets()[0]; // Assuming data is in the first sheet
  if (!sourceSheet) {
    Logger.log('Error: No sheet found in source spreadsheet');
    return;
  }
  
  var data = sourceSheet.getDataRange().getValues();
  Logger.log('Retrieved ' + data.length + ' rows from source sheet');
  
  if (data.length < 2) {
    Logger.log('Error: Source sheet is empty or contains only headers');
    return;
  }
  
  var headers = data[0];
  Logger.log('Source headers: ' + headers.join(', '));
  var dataRows = data.slice(1);  // Remove header row
  
  // Sort data by date
  var dateIndex = headers.indexOf('Date(UTC)');
  if (dateIndex === -1) {
    Logger.log('Error: Unable to find Date(UTC) column in the source data');
    return;
  }
  
  dataRows.sort(function(a, b) {
    var dateA = new Date(a[dateIndex]);
    var dateB = new Date(b[dateIndex]);
    return dateA - dateB;
  });
  
  Logger.log('Data sorted by date');
  
  var transferredCount = 0;
  var errorCount = 0;
  
   dataRows.forEach(function(row, index) {
    var addressIndex = headers.indexOf('Address');
    var sourceIndex = headers.indexOf('Source');
    
    if (addressIndex === -1 || sourceIndex === -1) {
      Logger.log('Error: Unable to find Address or Source column in the source data');
      return;
    }
    
    var address = row[addressIndex];
    var source = row[sourceIndex];
    
    Logger.log('Processing row ' + (index + 2) + ': Address = ' + address + ', Source = ' + source + ', Date = ' + row[dateIndex]);
    
    var matchedVenue = findMatchingVenue(address);
    
    if (matchedVenue && matchedVenue.sheets[source]) {
      var targetSpreadsheetId = matchedVenue.spreadsheetId;
      var targetSheetName = matchedVenue.sheets[source];
      
      try {
        var mappedRow;
        if (targetSpreadsheetId === LOCATION_MAPPING['ΔΑΕΑΝ'].spreadsheetId) {
          mappedRow = mapRowToTargetStructureDAEAN(row, headers, source);
        } else if (targetSpreadsheetId === LOCATION_MAPPING['Hotel Papas'].spreadsheetId) {
          mappedRow = mapRowToTargetStructureHotelPapas(row, headers, source);
        } else {
          throw new Error('Unknown spreadsheet ID: ' + targetSpreadsheetId);
        }
        
        appendRowToSheet(targetSpreadsheetId, targetSheetName, TARGET_COLUMNS, mappedRow);
        Logger.log('Transferred row ' + (index + 2) + ' to ' + targetSheetName);
        transferredCount++;
      } catch (e) {
        Logger.log('Error transferring row ' + (index + 2) + ': ' + e.toString());
        errorCount++;
      }
    } else {
      Logger.log('No mapping found for row ' + (index + 2) + ': ' + address + ', ' + source);
      if (!matchedVenue) {
        Logger.log('No matching venue found for address: ' + address);
      } else if (!matchedVenue.sheets[source]) {
        Logger.log('No sheet found for source ' + source + ' in matched venue');
      }
      errorCount++;
    }
  });
  
  Logger.log('Data transfer completed. Transferred rows: ' + transferredCount + ', Errors: ' + errorCount);
}


function findMatchingVenue(address) {
  for (var loc in LOCATION_MAPPING) {
    for (var venue in LOCATION_MAPPING[loc].venues) {
      if (address && address.includes(LOCATION_MAPPING[loc].venues[venue].address)) {
        Logger.log('Matched venue: ' + venue + ' for address: ' + address);
        return {
          spreadsheetId: LOCATION_MAPPING[loc].spreadsheetId,
          sheets: LOCATION_MAPPING[loc].venues[venue].sheets
        };
      }
    }
  }
  Logger.log('No matching venue found for address: ' + address);
  return null;
}

function mapRowToTargetStructureDAEAN(row, headers, source) {
  switch(source) {
    case 'tripadvisor':
      return [
        '',
        row[headers.indexOf('Review ID')],
        row[headers.indexOf('Reviewer')],
        row[headers.indexOf('Review Link')],
        row[headers.indexOf('Title')],
        row[headers.indexOf('Comment')],
        row[headers.indexOf('Review Language')],
        row[headers.indexOf('Star Rating')],
        row[headers.indexOf('Date(UTC)')],
        '',
        row[headers.indexOf('Reply Text')]
      ];
    default:
      throw new Error('Unknown source for ΔΑΕΑΝ: ' + source);
  }
}

function mapRowToTargetStructureHotelPapas(row, headers, source) {
  switch(source) {
    case 'Booking Index':
      return [
        '',
        row[headers.indexOf('Reviewer')],
        row[headers.indexOf('Date(UTC)')],
        row[headers.indexOf('Star Rating')],
        '',
        row[headers.indexOf('Comment')],
        '',
        row[headers.indexOf('Reply Text')]
      ];
    case 'google':
      return [
        row[headers.indexOf('Date(UTC)')],
        row[headers.indexOf('Reviewer')],
        row[headers.indexOf('Comment')],
        '',
        '',        
        row[headers.indexOf('Star Rating')],
        row[headers.indexOf('Reply Text')]
      ];
      case 'tripadvisor':
      return [
        row[headers.indexOf('Date(UTC)')],
        row[headers.indexOf('Reviewer')],
        row[headers.indexOf('Title')],
        row[headers.indexOf('Comment')],
        '',
        '',
        row[headers.indexOf('Star Rating')],
        row[headers.indexOf('Reply Text')]
      ];
    default:
      throw new Error('Unknown source for Hotel Papas: ' + source);
  }
}


function appendRowToSheet(spreadsheetId, sheetName, headers, rowData) {
  try {
    var spreadsheet = SpreadsheetApp.openById(spreadsheetId);
    var sheet = spreadsheet.getSheetByName(sheetName);
    
    if (!sheet) {
      Logger.log('Sheet not found: ' + sheetName + ' in spreadsheet: ' + spreadsheetId);
      return;
    }
    
    var lastRow = sheet.getLastRow();
    if (lastRow === 0) {
      // If sheet is empty, add headers first
      sheet.appendRow(headers);
      lastRow = 1;
    }
    
    sheet.appendRow(rowData);
  } catch (e) {
    Logger.log('Error in appendRowToSheet: ' + e.toString());
    throw e;
  }
}