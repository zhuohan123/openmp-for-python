#include <cstdlib>

#include "OMP.h"
#include "PY.h"
#include "Core.h"

int NofBlock 	= 0;
int NofLock 	= 0;
int NofLog		= 0;
int NofCode		= 0;
int NofNode		= 0;

string PY_code, PY_log, OMP_log, OUT_code;
vector< vector<pair<int, string> > > addCode;
vector<string> Code, Log;
vector<Block_t*> Block;
struct Node_t *root;

map<int, paraFor_t*> line2For;

void initialize()
{
	addCode.clear();
	Code.clear();
	Log.clear();
	Block.clear();
	root = NULL;
	line2For.clear();
}

void ParseArgv(int argc, char **argv)
{
	if (argc != 5)
	{
		fprintf(stderr, "Usage: %s PY_code PY_log OMP_log OUT_code\n", argv[0]);
		exit(-1);
	}
	PY_code 	= (string)argv[1];
	PY_log  	= (string)argv[2];
	OMP_log 	= (string)argv[3];
	OUT_code 	= (string)argv[4];
}

int main(int argc, char **argv)
{
	initialize();
	ParseArgv(argc, argv);
	InputOMP(OMP_log);
	InputPY(PY_code, PY_log);
	changeVariable(root);
	OpenMPforPython();
	output(OUT_code);

	return 0;
}