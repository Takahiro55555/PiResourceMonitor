/**
 * @OnlyCurrentDoc
 */

function doPost(e) {
    var ss = SpreadsheetApp.getActiveSpreadsheet(); // スプレッドシートオブジェクトを取得
    var host_name = e.parameter.host_name;
    if (host_name == undefined) {
        return ContentService.createTextOutput("ERROR: host_name is not defined.");
    }
    if (e.parameter.max_row == undefined) {
        return ContentService.createTextOutput("ERROR: max_row is not defined.");
    }
    var sheet = getSheet(ss, host_name);
    var last_row = sheet.getLastRow();
    if (last_row === 0) {
        // カラム名が設定されていない場合設定する
        setColumnName(sheet, e.parameter);
    }
    insertRow(sheet, e.parameter);
    return ContentService.createTextOutput("OK");
}

/* ホスト名からシートオブジェクトを作成又は、取得する */
function getSheet(ss, host_name) {
    var sheet = ss.getSheetByName(host_name); // シートを指定
    // 当該シートが存在しない場合、新規作成
    if (sheet === null) {
        sheet = ss.insertSheet(host_name);
    }
    return sheet;
}

/* データを設定する */
function insertRow(sheet, data) {
    var col = 1;
    var row = sheet.getLastRow() + 1;
    for (key in data) {
        sheet.getRange(row, col).setValue(data[key]);
        col++;
    }

    var last_row = sheet.getLastRow();
    var delete_rows_num = last_row - Number(data.max_row) - 1;
    if (delete_rows_num > 0) {
        // 先頭行を削除
        sheet.deleteRows(2, delete_rows_num); // カラム名の行を考慮
    }
}

/* カラム名を設定する */
function setColumnName(sheet, data) {
    var row = 1;
    var col = 1;
    for (key in data) {
        sheet.getRange(row, col).setValue(key);
        col++;
    }
}