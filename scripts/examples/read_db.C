#include <TSQLServer.h>
#include <TSQLResult.h>
#include <TSQLRow.h>

// Simple example macro to read database using ROOT TSQL

void read_db()
{

  TSQLServer *db = TSQLServer::Connect("mysql://hallcdb.jlab.org/c-rcdb","rcdb","");
  cout << db->ServerInfo() << endl;

  TSQLResult* res;
  TSQLRow *row;
  
  TString query_str1 = "select run_number FROM `c-rcdb`.conditions, `c-rcdb`.condition_types ";
  TString query_str2 = "where conditions.condition_type_id=condition_types.id and name='run_type' and text_value='Production'";

  TString query_str = query_str1 + query_str2;
  res = db->Query(query_str);
  int nrows = res->GetRowCount();
  int nfields = res->GetFieldCount();

  for(int i=0; i< nrows; i++) {
    row = res->Next();
    for(int j=0; j< nfields; j++) {
      cout << row->GetField(j) << endl;
    }
  }

  delete row;
  delete res;
  delete db;
}
