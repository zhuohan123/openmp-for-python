#ifndef TOOLKIT_H
#define TOOLKIT_H

#include <string>
#include <sstream>
#include <fstream>
#include <iostream>
#include <vector>

using namespace std;

const int INF = (1<<30)-1;

const string dictKeyWord = "_dict";
const string blockKeyWord = "_block";

string ItoS(int x);
int StoI(string x);
string strip(string s);
bool begin_with(string s, string sub);
bool end_with(string s, string sub);
int countNofSpace(string code);
string parseLog(string log, int k);
void output(string);

extern vector< vector<pair<int, string> > > addCode;
extern vector<string> Code;
extern int NofCode;

#endif