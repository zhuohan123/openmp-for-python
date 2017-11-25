#ifndef OMP_H
#define OMP_H

#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <map>

using namespace std;

struct paraFor_t
{
	int lineId;
	int sLine, tLine;
	int lockId;
	vector<string> operCh;			// for reduction
	vector<string> varName;
	string mode;					// for static/dynamic
	bool nowait;
	paraFor_t(int _lindId);
};

struct Critical_t
{
	int lockId;
	int sLine, tLine;
	Critical_t(int _sLine);
};

struct Section_t
{
	int sLine, tLine;
	Section_t(int _sLine);
};

struct Sections_t
{
	int sLine, tLine;
	bool nowait;
	vector<Section_t> section;
	Sections_t(int _sLine);
};

struct Block_t
{
	int numThreads;
	int sLine, tLine;
	vector<int> barrier;
	set<string> privateVar;
	vector<paraFor_t> paraFor;
	vector<Critical_t> critical;
	vector<Sections_t> sections;
	Block_t(int _sLine);
};

void InputOMP(string OMP_log);

extern int NofLock;
extern int NofBlock;
extern vector<Block_t*> Block;
extern map<int, paraFor_t*> line2For;

#endif