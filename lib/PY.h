#ifndef PY_H
#define PY_H

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stack>
#include <map>
#include <set>

#include "OMP.h"
#include "Toolkit.h"

using namespace std;

struct Node_t
{
	int nodeId;
	string name, space;
	int sLine, tLine;
	vector<int> logId;
	vector<Node_t*> child;
	set<string> local;
	set<string> global;
	Node_t *father;

	Node_t(string _name, int _sLine, Node_t *_father);
	int build(int sLogL);
};

void InputPY(string PY_code, string PY_log);

extern int NofLog;
extern int NofCode;
extern int NofNode;
extern int NofLock;
extern vector<string> Log;
extern vector<string> Code;
extern vector< vector<pair<int, string> > > addCode;
extern struct Node_t *root;
extern map<int, paraFor_t*> line2For;

#endif