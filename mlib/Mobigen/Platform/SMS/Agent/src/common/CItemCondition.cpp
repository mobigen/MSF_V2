
#include "CItemCondition.h"


CItemCondition::CItemCondition()
{
	m_index = 0;
	m_element = 0;
	m_instName = "N/A";
	m_condition = "N/A";
	m_severity = "N/A";
	m_parsecondition.count = 0;
	isChange = true;
}

CItemCondition::~CItemCondition()
{
}

bool CItemCondition::isOverThreshold(unsigned long value)
{
	return isOverThreshold((double) value);
}

bool CItemCondition::isOverThreshold(std::string value)
{
	return isOverThreshold((char *)value.c_str());
}

bool CItemCondition::isOverThreshold(int val)
{
	return isOverThreshold((double) val);
}

bool CItemCondition::isOverThreshold(long val)
{
	return isOverThreshold((double) val);
}

bool CItemCondition::isOverThreshold(double val)
{
	int i=1;
	bool ret=false;
	char temp[1024];
	if(m_parsecondition.count == 0 || isChange) {
		m_parsecondition.count = 0;
		isChange = false;
		memset(temp, 0x00, sizeof(temp));
		strcpy(temp, getCondition().c_str());
		parseCondition(temp);
		if(m_parsecondition.count == 0)
			return false;
	}
	ret = checkCondition(&m_parsecondition.item[0], val);
	for(;i<m_parsecondition.count;i++){
		ret = checkCondition(ret, m_parsecondition.c[i], &m_parsecondition.item[i], val);
	}

	return ret;
}

bool CItemCondition::isOverThreshold(char *val)
{
	int i=1;
	bool ret=false;
	char temp[1024];
	if(m_parsecondition.count == 0 || isChange ){
		m_parsecondition.count = 0;
		isChange = false;
		memset(temp, 0x00, sizeof(temp));
		strcpy(temp, getCondition().c_str());
		parseCondition(temp);
		if(m_parsecondition.count == 0)
			return false;
	}
	ret = checkCondition(&m_parsecondition.item[0], val);
	for(;i<m_parsecondition.count;i++){
		ret = checkCondition(ret, m_parsecondition.c[i], &m_parsecondition.item[i], val);
	}

	return ret;
}

bool CItemCondition::checkOperator(char *op)
{
	char *p = op, *q=NULL;
	int len=0;
	st_conditem item;

	memset(&item, 0x00, sizeof(item));
	q = p;
	q += (strlen(p)-1);
	while(q != 0x00 && (isspace(*q) || *q == '\042')){ *q = '\0'; q--; }
	while(isspace(*p) || *p == '\"') p++;

	if(strncmp(p, ">=", 2)==0){
		item.opcode = COND_OPCODE_EGT;
		item.type = 'D';
		p+=2; while(isspace(*p) || *p == '\"' ) p++;
		item.val.d = atof(p);
	}else if(strncmp(p, "<=", 2)==0){
		item.opcode = COND_OPCODE_ELT;
		item.type = 'D';
		p+=2; while(isspace(*p) || *p == '\"' ) p++;
		item.val.d = atof(p);
	}else if(strncmp(p, "==", 2)==0){
		item.opcode = COND_OPCODE_EQ;
		item.type = 'D';
		p+=2; while(isspace(*p) || *p == '\"' ) p++;
		item.val.d = atof(p);
	}else if(strncmp(p, "!=", 2)==0){
		item.opcode = COND_OPCODE_NEQ;
		item.type = 'D';
		p+=2; while(isspace(*p) || *p == '\"' ) p++;
		item.val.d = atof(p);
	}else if(strncmp(p, ">>", 2)==0){
		item.opcode = COND_OPCODE_SUBSTR;
		item.type = 'S';
		p+=2; while(isspace(*p) || *p == '\"' ) p++;
		strcpy(item.val.s, p);
	}else if(strncmp(p, "<<", 2)==0){
		item.opcode = COND_OPCODE_NSUBSTR;
		item.type = 'S';
		p+=2; while(isspace(*p) || *p == '\"' ) p++;
		strcpy(item.val.s, p);
	}else if(strncmp(p, ">", 1)==0){
		item.opcode = COND_OPCODE_GT;
		item.type = 'D';
		p+=1; while(isspace(*p) || *p == '\"' ) p++;
		item.val.d = atof(p);
	}else if(strncmp(p, "<", 1)==0){
		item.opcode = COND_OPCODE_LT;
		item.type = 'D';
		p+=1; while(isspace(*p) || *p == '\"' ) p++;
		item.val.d = atof(p);
	}else{
		return false;
	}

	memcpy(&m_parsecondition.item[m_parsecondition.count], &item, sizeof(item));
	m_parsecondition.count++;
	return true;
}

bool CItemCondition::checkCondition(st_conditem *item, double val)
{

	switch(item->opcode){
		case COND_OPCODE_EGT: /* egt */
			if(val >= item->val.d) return true;
			else return false;
		case COND_OPCODE_GT: /* gt */
			if(val > item->val.d) return true;
			else return false;
		case COND_OPCODE_ELT: /* elt */
			if(val <= item->val.d) return true;
			else return false;
		case COND_OPCODE_LT: /* lt */
			if(val < item->val.d) return true;
			else return false;
		case COND_OPCODE_EQ: /* eq */
			if(val == item->val.d) return true;
			else return false;
		case COND_OPCODE_NEQ: /* neq */
			if(val != item->val.d) return true;
			else return false;
		case COND_OPCODE_SUBSTR: /* substr */
			return false;
		case COND_OPCODE_NSUBSTR: /* not substr */
			return false;
		default:
			return false;
	}
	return false;
}

bool CItemCondition::checkCondition(st_conditem *item, char *val)
{
	switch(item->opcode){
		case COND_OPCODE_EGT: /* egt */
			return false;
		case COND_OPCODE_GT: /* gt */
			return false;
		case COND_OPCODE_ELT: /* elt */
			return false;
		case COND_OPCODE_LT: /* lt */
			return false;
		case COND_OPCODE_EQ: /* eq */
			if(strcmp(val, item->val.s)==0) return true;
			else return false;
		case COND_OPCODE_NEQ: /* !eq */
			return false;
		case COND_OPCODE_NSUBSTR: /* not substr */
			if(!strstr(val, item->val.s)) return true;
			else return false;
		case COND_OPCODE_SUBSTR: /* substr */
			if(strstr(val, item->val.s)) return true;
			else return false;
		default:
			return false;
	}
	return false;
}

bool CItemCondition::checkCondition(bool b, char c, st_conditem *item, double val)
{
	bool ret = false;

	ret = checkCondition(item, val);
	switch(c){
		case '1' : /* AND */
			if(b==true && ret == true) return true;
			else return false;
		case '2' : /* OR */
			if(b==true || ret == true) return true;
			else return false;
		default:
			return false;
	}

	return ret;
}

bool CItemCondition::checkCondition(bool b, char c, st_conditem *item, char *val)
{
	bool ret = false;

	ret = checkCondition(item, val);

	switch(c){
		case '1' : /* AND */
			if(b==true && ret == true) return true;
			else return false;
		case '2' : /* OR */
			if(b==true || ret == true) return true;
			else return false;
		default:
			return false;
	}

	return ret;
}

void CItemCondition::parseCondition(char *s)
{
	char *_p, *p=NULL, *q=NULL, *r=NULL, str[1024];
	char c;

//printf("condition[%s]\n", s);

	_p = s;
	p = (char *)strstr(_p, "AND");
	q = (char *)strstr(_p, "OR");
	if(p!=NULL || q!=NULL){
		do {
			if(p!=NULL && q!=NULL){
				if(strlen(p) > strlen(q)){
					r = p;
					c = '1';
				} else {
					r = q;
					c = '2';
				}
			}else if(p != NULL){
				r = p;
				c = '1';
			}else if(q != NULL){
				r = q;
				c = '2';
			}
			memset(str, 0x00, sizeof(str));
			strncpy(str, _p, strlen(_p)-strlen(r));
			if(checkOperator(str)==true)
				m_parsecondition.c[m_parsecondition.count] = c;

			if(c=='1') r+=3;
			else r+=2;
			_p = r;
			p = (char *)strstr(_p, "AND");
			q = (char *)strstr(_p, "OR");

		}while(p!=NULL || q!=NULL);

		memset(str, 0x00, sizeof(str));
		strcpy(str, _p);
		if(checkOperator(str)==true) m_parsecondition.c[m_parsecondition.count]=c;
	}else{
		memset(str, 0x00, sizeof(str));
		strcpy(str, s);
		checkOperator(str);
	}
	return;
}

void deleteCItemCondition(void *d)
{
	CItemCondition *cond = (CItemCondition *)d;
	if(cond != NULL) delete cond;
}

