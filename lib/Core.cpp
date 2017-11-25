#include "Core.h"

#include "assert.h"

int findVariable(Node_t *P, string name)
{
	while (P && P->local.find(name) == P->local.end())
		P = P->father;
	if (P) return P->nodeId;
	return -1;
}

void changeVariable(Node_t *P)
{
	cerr << "changeVariable " << P->name << endl;

	int n = P->logId.size();
	int comDep = 0, lamDep = 0;
	set<string> lamArg;
	stack<int> forLine;
	map<string,string> forVar;
	int codeL = -1, span = 0;
	int ptrBlock = 0;
	for (int i = 0; i < n; ++i)
	{
		string log = Log[P->logId[i]];
		string type = parseLog(log, 0);
		if (type == "arg" || type == "vararg" || type == "kwarg")
		{
			if (lamDep)
				lamArg.insert(parseLog(log, 1));
			else
			{
				P->local.insert(parseLog(log, 1));
				string name = parseLog(log, 1);
				string tmpstr = P->space + dictKeyWord + ItoS(P->nodeId) + "['" + name + "']=" + name;
				addCode[P->sLine].push_back(make_pair(0, tmpstr));
			}
		} else
		if (type == "global")
		{
			P->global.insert(parseLog(log, 1));
		} else
		if (type == "comprehension")
		{
			if (parseLog(log, 1) == "start")
				++comDep;
			else
				--comDep;
		} else
		if (type == "lambda")
		{
			if (parseLog(log, 1) == "start")
			{
				++lamDep;
				lamArg.clear();
			}
			else
				--lamDep;
		} else
		if (type == "for")
		{
			if (parseLog(log, 1) == "begin")
			{
				int line = StoI(parseLog(log, 2)) - 1;
				forLine.push(line);
				map<int,paraFor_t*>::iterator it = line2For.find(line);
				if (it != line2For.end())
				{
					paraFor_t *ptr = it->second;
					int NofVar = ptr->varName.size();
					for (int j = 0; j < NofVar; ++j)
						forVar.insert(make_pair(ptr->varName[j], "OMP_REDUCTION_VAR_" + ItoS(ptr->lockId) + "_" + ItoS(j)));
				}
			} 
			else
			{
				int line = forLine.top();
				forLine.pop();
				map<int,paraFor_t*>::iterator it = line2For.find(line);
				if (it != line2For.end())
				{
					paraFor_t *ptr = it->second;
					int NofVar = ptr->varName.size();
					for (int j = 0; j < NofVar; ++j)
					{
						forVar.erase(ptr->varName[j]);
						string rpStr;
						if (P->local.find(ptr->varName[j]) != P->local.end())
							rpStr = dictKeyWord+ItoS(P->nodeId)+"['"+ptr->varName[j]+"']";
						else
						{
							int id = findVariable(P, ptr->varName[j]);
							if (id == -1) continue;
							rpStr = dictKeyWord+ItoS(id)+"['"+ptr->varName[j]+"']";
						}
						ptr->varName[j] = rpStr;
					}
				}
			}
		} else
		if (type == "variable")
		{
			int tmpCodeL = StoI(parseLog(log, 1));
			if (tmpCodeL != codeL)
			{
				span = 0;
				codeL = tmpCodeL;
				while (ptrBlock < NofBlock && codeL > Block[ptrBlock]->tLine)
					++ptrBlock;
			}
			int col = StoI(parseLog(log, 2));
			string name = parseLog(log, 3);
			string act = parseLog(log, 4);
			if (forVar.find(name) != forVar.end())
			{
				string rpStr = forVar[name];
				Code[codeL].replace(col+span, name.length(), rpStr);
				span += rpStr.length() - name.length();
				continue;
			}
			if (P->name == "global") continue;
			if (comDep && act == "store") continue;
			if (lamDep && lamArg.find(name) != lamArg.end()) continue;
			if (P->global.find(name) != P->global.end()) continue;
			if (ptrBlock < NofBlock && Block[ptrBlock]->sLine < codeL
				&& Block[ptrBlock]->privateVar.find(name) != Block[ptrBlock]->privateVar.end()) continue;
			if (act == "store" || act == "del")
			{
				if (act == "store")
					P->local.insert(name);
				else
					P->local.erase(name);
				string rpStr = dictKeyWord+ItoS(P->nodeId)+"['"+name+"']";
				Code[codeL].replace(col+span, name.length(), rpStr);
				span += rpStr.length() - name.length();
			} else
			if (act == "load")
			{
				int id = findVariable(P, name);
				if (id == -1) continue;
				string rpStr = dictKeyWord+ItoS(id)+"['"+name+"']";
				Code[codeL].replace(col+span, name.length(), rpStr);
				span += rpStr.length() - name.length();
			}
		}
	}
	n = P->child.size();
	for (int i = 0; i < n; ++i)
		changeVariable(P->child[i]);
}

Node_t *findBelong(Node_t *P, int line)
{
	if (line < P->sLine || P->tLine < line)
		return NULL;
	int n = P->child.size();
	for (int i = 0; i < n; ++i)
	{
		Node_t *ret = findBelong(P->child[i], line);
		if (ret) return ret;
	}
	return P;
}

void AddThreading(int line, string space, string funName, int numThreads)
{
	string tmpstr;
	tmpstr = space + "omp.parallel_run(" + funName + "," + ItoS(numThreads) + ")";
	addCode[line].push_back(make_pair(0, tmpstr));
}

void OpenMPforPython()
{
	cerr << "paralleling" << endl;
	for (int i = 0; i < NofBlock; ++i)
	{
		string space = "";
		int tmp = countNofSpace(Code[Block[i]->sLine+1]);
		for (int j = 0; j < tmp; ++j)
			space.push_back(' ');

		/* parallel */
		cerr << "parallel" << endl;
		string tmpstr = space + "def " + blockKeyWord + ItoS(i) + "():";
		addCode[Block[i]->sLine].push_back(make_pair(0, tmpstr));
		Node_t *father = findBelong(root, Block[i]->sLine);
		if (father->name != "global")
			for (set<string>::iterator it = father->global.begin(); it != father->global.end(); ++it)
			{
				tmpstr = space + "    " + "global " + *it;
				addCode[Block[i]->sLine].push_back(make_pair(0, tmpstr));
			}
		else
		{
			// global for global
		}
		for (int j = Block[i]->sLine+1; j < Block[i]->tLine; ++j)
			Code[j] = "    " + Code[j];
		AddThreading(Block[i]->tLine, space, blockKeyWord+ItoS(i), Block[i]->numThreads);

		/* sections */
		int NofSections = Block[i]->sections.size();
		for (int id1 = 0; id1 < NofSections; ++id1)
		{
			int sLine = Block[i]->sections[id1].sLine;
			int NofSection = Block[i]->sections[id1].section.size();
			tmpstr = space + "    for OMP_SECTIONS_ID in omp.prange(" + ItoS(NofSection) + "):";
			addCode[sLine].push_back(make_pair(0, tmpstr));
			for (int id2 = 0; id2 < NofSection; ++id2)
			{
				int sLine = Block[i]->sections[id1].section[id2].sLine;
				int tLine = Block[i]->sections[id1].section[id2].tLine;
				string tmpstr = space + "        if OMP_SECTIONS_ID == " + ItoS(id2) + ":";
				addCode[sLine].push_back(make_pair(0, tmpstr));
				for (int j = sLine+1; j < tLine; ++j)
					Code[j] = "        " + Code[j];
			}
			int tLine = Block[i]->sections[id1].tLine;
			if (Block[i]->sections[id1].nowait == false)
			{
				tmpstr = space + "    omp.barrier()";
				addCode[tLine].push_back(make_pair(1, tmpstr));
			}
		}

		/* for */
		int NofFor = Block[i]->paraFor.size();
		for (int id = 0; id < NofFor; ++id)
		{
			int line = Block[i]->paraFor[id].sLine;
			int NofVar = Block[i]->paraFor[id].varName.size();
			if (NofVar != 0)
			{
				for (int j = 0; j < NofVar; ++j)
				{
					tmpstr = space + "    OMP_REDUCTION_VAR_" + ItoS(Block[i]->paraFor[id].lockId) + 
							 "_" + ItoS(j) + " = omp.reduction_init('" + Block[i]->paraFor[id].operCh[j] + "')";
					addCode[line-1].push_back(make_pair(0, tmpstr));
				}
			}
			int spos = Code[line].find(" in ") + 4;
			int tpos = Code[line].find(":") - 1;
			string subline = strip(Code[line].substr(spos, tpos-spos+1));
			string str = (Block[i]->paraFor[id].mode == "dynamic")? "omp.drange" : "omp.prange";
			if (begin_with(subline, "xrange("))
				Code[line].replace(Code[line].find("xrange"), 6, str);
			else if (begin_with(subline, "range("))
				Code[line].replace(Code[line].find("range"), 5, str);
			else
			{
				str = (Block[i]->paraFor[id].mode == "dynamic")? "omp.dlist(" : "omp.plist(";
				Code[line].insert(tpos+1, ")");
				Code[line].insert(spos, str);
			}
			int tLine = Block[i]->paraFor[id].tLine;
			if (NofVar != 0)
			{
				for (int j = 0; j < NofVar; ++j)
				{
					tmpstr = space + "    omp.set_internal_lock(" + ItoS(Block[i]->paraFor[id].lockId) + ")";
					addCode[tLine].push_back(make_pair(0, tmpstr));
					tmpstr = space + "    " + Block[i]->paraFor[id].varName[j] + 
							 " = omp.reduction('" + Block[i]->paraFor[id].operCh[j] + "'," + 
							 Block[i]->paraFor[id].varName[j] + "," + "OMP_REDUCTION_VAR_" +
							 ItoS(Block[i]->paraFor[id].lockId) + "_" + ItoS(j) + ")";
					addCode[tLine].push_back(make_pair(1, tmpstr));
					tmpstr = space + "    omp.unset_internal_lock(" + ItoS(Block[i]->paraFor[id].lockId) + ")";
					addCode[tLine].push_back(make_pair(2, tmpstr));
				}
			}
			if (Block[i]->paraFor[id].nowait == false)
			{
				tmpstr = space + "    omp.barrier()";
				addCode[tLine].push_back(make_pair(3, tmpstr));
			}
		}

		/* barrier */
		int NofBarrier = Block[i]->barrier.size();
		for (int id = 0; id < NofBarrier; ++id)
		{
			int line = Block[i]->barrier[id];
			tmpstr = space + "    omp.barrier()";
			addCode[line].push_back(make_pair(0, tmpstr));
		}

		/* critical */
		int NofCritical = Block[i]->critical.size();
		for (int id = 0; id < NofCritical; ++id)
		{
			int sLine = Block[i]->critical[id].sLine;
			int tLine = Block[i]->critical[id].tLine;
			tmpstr = space + "        omp.set_internal_lock(" + ItoS(Block[i]->critical[id].lockId) + ")";
			addCode[sLine].push_back(make_pair(0, tmpstr));
			tmpstr = space + "        omp.unset_internal_lock(" + ItoS(Block[i]->critical[id].lockId) + ")";
			addCode[tLine-1].push_back(make_pair(0, tmpstr));
		}
	}
}