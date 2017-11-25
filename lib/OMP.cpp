#include "OMP.h"
#include "Toolkit.h"

paraFor_t::paraFor_t(int _lineId)
{
	lineId = _lineId;
	sLine  = _lineId+1;
	lockId = NofLock++;
	operCh.clear();
	varName.clear();
	nowait = false;
	mode = "";
}

Critical_t::Critical_t(int _sLine)
{
	lockId = NofLock++;
	sLine = _sLine;
	tLine = 0;
}

Section_t::Section_t(int _sLine)
{
	sLine = _sLine;
}

Sections_t::Sections_t(int _sLine)
{
	section.clear();
	sLine = _sLine;
	tLine = 0;
	nowait = false;
}

Block_t::Block_t(int _sLine)
{
	numThreads = 0;
	sLine = _sLine;
	tLine = 0;
	paraFor.clear();
	critical.clear();
	sections.clear();
	barrier.clear();
	privateVar.clear();
}

void InputOMP(string OMP_log)
{
	cerr << "Input OMP" << endl;

	Block_t *tmpBlock = NULL;
	ifstream fin(OMP_log.c_str());
	int ForOrSect = 0;
	string line;
	while (!fin.eof())
	{
		getline(fin, line);
		if (line == "") continue;
		string type = parseLog(line, 0);
		if (type == "parallel")
		{
			if (parseLog(line, 2) == "begin")
				tmpBlock = new Block_t(StoI(parseLog(line, 1)));
			else
			{
				tmpBlock->tLine = StoI(parseLog(line, 1));
				Block.push_back(tmpBlock);
				tmpBlock = NULL;
			}
		} else
		{
			if (!tmpBlock) continue;
			if (type == "private_var")
				tmpBlock->privateVar.insert(parseLog(line, 1));
			else if (type == "num_threads")
				tmpBlock->numThreads = StoI(parseLog(line, 1));
			else if (type == "nowait")
			{
				if (parseLog(line, 1) == "False") continue;
				if (ForOrSect == 1)
				{
					int id = tmpBlock->paraFor.size()-1;
					tmpBlock->paraFor[id].nowait = true;
				}
				else if (ForOrSect == 2)
				{
					int id = tmpBlock->sections.size()-1;
					tmpBlock->sections[id].nowait = true;
				}
			}
			else if (type == "barrier")
				tmpBlock->barrier.push_back(StoI(parseLog(line, 1)));
			else if (type == "for")
			{
				ForOrSect = 1;
				int lineId = StoI(parseLog(line, 1));
				tmpBlock->paraFor.push_back(paraFor_t(lineId));
				int tmp = tmpBlock->paraFor.size() - 1;
				line2For.insert(make_pair(lineId, &tmpBlock->paraFor[tmp]));
			}
			else if (type == "reduction")
			{
				int id = tmpBlock->paraFor.size()-1;
				tmpBlock->paraFor[id].operCh.push_back(parseLog(line, 1));
				tmpBlock->paraFor[id].varName.push_back(parseLog(line, 2));
			} 
			else if (type == "scheduling_type")
			{
				int id = tmpBlock->paraFor.size()-1;
				tmpBlock->paraFor[id].mode = parseLog(line, 1);
			}
			else if (type == "critical")
			{
				if (parseLog(line, 2) == "begin")
					tmpBlock->critical.push_back(Critical_t(StoI(parseLog(line, 1))));
				else
				{
					int id = tmpBlock->critical.size()-1;
					tmpBlock->critical[id].tLine = StoI(parseLog(line, 1));
				}
			}
			else if (type == "sections")
			{
				ForOrSect = 2;
				if (parseLog(line, 2) == "begin")
					tmpBlock->sections.push_back(Sections_t(StoI(parseLog(line, 1))));
				else
				{
					int id = tmpBlock->sections.size()-1;
					tmpBlock->sections[id].tLine = StoI(parseLog(line, 1));
				}
			}
			else if (type == "section")
			{
				int id1 = tmpBlock->sections.size()-1;
				if (parseLog(line, 2) == "begin")
					tmpBlock->sections[id1].section.push_back(Section_t(StoI(parseLog(line, 1))));
				else
				{
					int id2 = tmpBlock->sections[id1].section.size()-1;
					tmpBlock->sections[id1].section[id2].tLine = StoI(parseLog(line, 1));
				}
			}
		}
	}
	NofBlock = Block.size();
	cerr << "NofBlock = " << NofBlock << endl;

	fin.close();
}