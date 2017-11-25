#include "PY.h"
#include "Toolkit.h"

Node_t::Node_t(string _name, int _sLine, Node_t *_father)
{
	cerr << "new Node " << _name << endl;
	nodeId = NofNode++;
	name = _name;
	sLine = _sLine;
	father = _father;
	if (name == "global")
	{ 	
		tLine = NofCode;
		space = "";
	}
	logId.clear();
	child.clear();
	local.clear();
	global.clear();
}

int Node_t::build(int sLogL)
{
	while (sLogL < NofLog)
	{
		while (sLogL < NofLog && parseLog(Log[sLogL], 0) != "function")
			logId.push_back(sLogL++);
		if (sLogL == NofLog) break;
		if (parseLog(Log[sLogL], 1) == "end")
		{
			tLine = StoI(parseLog(Log[sLogL], 3));
			int tmp = INF;
			for (int i = sLine+1; i < tLine; ++i)
				tmp = min(tmp, countNofSpace(Code[i]));
			space = "";
			for (int j = 0; j < tmp; ++j) 
				space.push_back(' ');
			string tmpstr = space + dictKeyWord + ItoS(nodeId) + "={}";
			addCode[sLine].push_back(make_pair(0, tmpstr));
			++sLogL; break;
		}
		else
		{
			Node_t *ch = new Node_t(parseLog(Log[sLogL], 2), StoI(parseLog(Log[sLogL], 3)), this);
			sLogL = ch->build(sLogL+1);
			child.push_back(ch);
		}
	}
	return sLogL;
}

void InputPY(string PY_code, string PY_log)
{
	cerr << "Input PY" << endl;

	string line;
	ifstream fin(PY_code.c_str());
	Code.push_back("");
	while (!fin.eof())
	{
		getline(fin, line);
		Code.push_back(line);
	}
	NofCode = Code.size();
	fin.close();

	stack<int> forLine;
	fin.open(PY_log.c_str());
	while (!fin.eof())
	{
		getline(fin, line);
		Log.push_back(line);
		if (parseLog(line, 0) == "for")
		{
			if (parseLog(line, 1) == "begin")
				forLine.push(StoI(parseLog(line, 2)) - 1);
			else
			{
				int lineId = forLine.top();
				forLine.pop();
				map<int,paraFor_t*>::iterator it = line2For.find(lineId);
				if (it != line2For.end())
				{
					paraFor_t *ptr = line2For[lineId];
					ptr->tLine = StoI(parseLog(line, 2)) - 1;
				}
			}
		}
	}
	NofLog = Log.size();
	fin.close();

	cerr << "NofCode = " << NofCode << endl;
	cerr << "NofLog = " << NofLog << endl;

	addCode.resize(NofCode);
	for (int i = 0; i < NofCode; ++i)
	{
		string line = strip(Code[i]);
		if (begin_with(line, "import ") && end_with(line, " omp"))
		{
			string tmpstr = "omp.set_num_of_internal_locks(" + ItoS(NofLock) + ")";
			addCode[i].push_back(make_pair(0, tmpstr));
			break;
		}
	}
	root = new Node_t("global", 0, NULL);
	root->build(0);
}