#include "Toolkit.h"

string ItoS(int x)
{
	string y;
	stringstream f;
	f << x; f >> y;
	return y;
}

int StoI(string x)
{
	int y;
	stringstream f;
	f << x; f >> y;
	return y;
}

string strip(string s)
{
	int l = 0, r = s.length()-1;
	while (l < r && (s[l] == ' ' || s[l] == '\t')) ++l;
	while (l < r && (s[r] == ' ' || s[r] == '\t')) --r;
	return s.substr(l, r-l+1);
}

bool begin_with(string s, string sub)
{
	int la = s.length();
	int lb = sub.length();
	if (la < lb) return false;
	for (int i = 0; i < lb; ++i)
		if (s[i] != sub[i]) return false;
	return true;
}

bool end_with(string s, string sub)
{
	int la = s.length();
	int lb = sub.length();
	if (la < lb) return false;
	for (int i = 1; i <= lb; ++i)
		if (s[la-i] != sub[lb-i]) return false;
	return true;
}

int countNofSpace(string code)
{
	int n = 0;
	while (code[n] == ' ' || code[n] == '\t')
		++n;
	return n;
}

string parseLog(string log, int k)
{
	log.push_back(' ');
	for (int i = 0; i < k; ++i)
		log.erase(0, log.find(" ")+1);
	return log.substr(0, log.find(" "));
}

void output(string OUT_code)
{
	cerr << "output()" << endl;

	ofstream fout(OUT_code.c_str());
	for (int i = 1; i < NofCode; ++i)
	{
		fout << Code[i] << endl;
		int n = addCode[i].size();
		for (int j = 0; j < n; ++j)
			for (int k = j+1; k < n; ++k)
				if (addCode[i][j].first > addCode[i][k].first)
					swap(addCode[i][j], addCode[i][k]);
		for (int j = 0; j < n; ++j)
			fout << addCode[i][j].second << endl;
	}
	fout.close();
}