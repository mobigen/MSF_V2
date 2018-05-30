#include<stdio.h>

int main()
{

	FILE *fp = fopen("/proc/stat", "r");

	char buf[BUFSIZ];

	while(fgets(buf, BUFSIZ, fp)) {
		printf("%s", buf);
	}

	fclose(fp);
}
