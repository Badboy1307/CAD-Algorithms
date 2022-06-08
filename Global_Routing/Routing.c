#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//#include <math.h>

//#define READFILE_TEST
#define DEBUG

#define BUFFER_LENGTH 100
#define MAX_INT 999999

// Using in data reading
typedef struct POINT_DATAS{
	int startx;
	int starty;
	int endx;
	int endy;
}datas;

// Using in BFS queue
typedef struct QUEUE_NODE{
	int x;
	int y;
	struct QUEUE_NODE *next;
}qnode;

// Using in Relax weight updating
typedef struct WEIGHT_MATRIX
{
	int before_x;
	int before_y;
	int weight;
	int length;
}wMatrix;

typedef struct ROUTE_MATRIX
{
	int next_x;
	int next_y;
}rMatrix;

// function define
int **mallocMatrix(int x, int y, int initVal);
datas *readFile(char const *fileName, int *netNumbers, int *capacity, int *gridDimx, int *gridDimy);
void Dijkstra(datas* data, int gridDimx, int gridDimy, int netNumbers, int capacity);
qnode *popAndPush(qnode *head, wMatrix *M, int **routingx, int **routingy, int capacity, int gridDimx, int gridDimy);
qnode *checkAndPush(qnode *head, qnode *checkNode, wMatrix *M, int **routingx, int **routingy, int capacity, int gridDimx, int gridDimy);
int compareEdgeWeight(qnode *originNode, qnode *nextNode, wMatrix *M, int **routingMap, int capacity, int gridDimx);
int countWeight(int **routingMap, int x, int y, int cpapacity);
void setLine(wMatrix *M, rMatrix *R, datas *data, int **routingx, int **routingy, int gridDimx);

int qSearch(qnode *head, int checkPosx, int checkPosy);
qnode *qPop(qnode *head, qnode *popElement);
qnode *qPush(qnode *head, int pushx, int pushy);
int power(int val, int exp);

//Test function
int main(int argc, char const *argv[])
{
	datas *data;
	int *capacity = (int*)malloc(sizeof(int));
	int *gridDimx = (int*)malloc(sizeof(int));
	int *gridDimy = (int*)malloc(sizeof(int));
	int *netNumbers = (int*)malloc(sizeof(int));

	data = readFile(argv[1], netNumbers, capacity, gridDimx, gridDimy);

	#ifdef READFILE_TEST
		printf("capacity = %d\n", *capacity);
		printf("grid dimention = %d*%d\n", *gridDimx, *gridDimy);
		printf("net numbers = %d\n", *netNumbers);
	#endif

	Dijkstra(data, *gridDimx, *gridDimy, *netNumbers, *capacity);

	return 0;
}

// Algorithm
void Dijkstra(datas* data, int gridDimx, int gridDimy, int netNumbers, int capacity)
{
	int **routingx = mallocMatrix(gridDimy , gridDimx , 0);
	int **routingy = mallocMatrix(gridDimy , gridDimx , 0);

	//netNumbers = 1;

	for (int i = 0; i < netNumbers; ++i)
	{
		// set queue and weight matrix and route matrix
		qnode *head = (qnode*)malloc(sizeof(qnode));
		rMatrix *R = (rMatrix*)malloc( gridDimx*gridDimy * sizeof(rMatrix));
		wMatrix *M = (wMatrix*)malloc( gridDimx*gridDimy * sizeof(wMatrix));
		for (int i = 0; i < gridDimx*gridDimy; ++i)
		{
			// initial weight matrix
			M[i].weight = MAX_INT;
			M[i].length = 0;
		}

		// set weight matrix start point data
		M[data[i].startx + gridDimx*data[i].starty].weight = 0;
		M[data[i].startx + gridDimx*data[i].starty].before_x = data[i].startx;
		M[data[i].startx + gridDimx*data[i].starty].before_y = data[i].starty;

		// push the start point into queue
		head->x = data[i].startx;		head->y = data[i].starty;
		head->next = NULL;

		while(head != NULL)
		{
			head = popAndPush(head, M, routingx, routingy, capacity, gridDimx, gridDimy);
		}

		// set weight matix next points
		setLine(M, R, data+i , routingx, routingy, gridDimx);

		/****************************************************************************************
		*										result output 									*
		*****************************************************************************************/
		
		// print net number, line length
		printf("%d %d\n", i, M[ data[i].endx + gridDimx*data[i].endy ].length );

		// c:checking point  n:next point
		int cx = data[i].startx;	int cy = data[i].starty;
		int nx, ny;
		
		while( cx != data[i].endx || cy != data[i].endy)
		{
			printf("%d %d ", cx, cy);
			nx = R[cx + gridDimx*cy].next_x;
			ny = R[cx + gridDimx*cy].next_y;
			printf("%d %d\n", nx, ny);
			cx = nx;	cy = ny;
		}
		

		free(M);
		free(R);
		free(head);
	}
}

qnode *popAndPush(qnode *head, wMatrix *M, int **routingx, int **routingy, int capacity, int gridDimx, int gridDimy)
{
	qnode *popElement = (qnode*)malloc(sizeof(qnode));
	head = qPop(head, popElement);
	head = checkAndPush(head, popElement, M, routingx, routingy, capacity, gridDimx, gridDimy);

	return head;
}

qnode *checkAndPush(qnode *head, qnode *checkNode, wMatrix *M, int **routingx, int **routingy, int capacity, int gridDimx, int gridDimy)
{
	qnode *up 	 = (qnode*)malloc(sizeof(qnode));
	qnode *down  = (qnode*)malloc(sizeof(qnode));
	qnode *right = (qnode*)malloc(sizeof(qnode));
	qnode *left  = (qnode*)malloc(sizeof(qnode));

	up->x = checkNode->x;		 up->y = checkNode->y +1;
	down->x = checkNode->x; 	 down->y = checkNode->y -1;
	right->x = checkNode->x +1;  right->y = checkNode->y;
	left->x = checkNode->x -1;	 left->y = checkNode->y;

	//printf("pop (%d %d)\n", checkNode->x, checkNode->y);


	// check adjacency node whether out range or not
	if (up->x >= 0 && up->x < gridDimx && up->y >= 0 && up->y < gridDimy)
	{
		// compare adjacency node's (original weight) with (start node's weight + edge weight)
		if ( compareEdgeWeight(checkNode, up, M, routingy, capacity, gridDimx) == 1 )
		{
			M[up->x + gridDimx*up->y].weight = M[checkNode->x + gridDimx*checkNode->y].weight + countWeight(routingy, up->x, up->y, capacity);
			M[up->x + gridDimx*up->y].length = M[checkNode->x + gridDimx*checkNode->y].length +1;
			M[up->x + gridDimx*up->y].before_x = checkNode->x;
			M[up->x + gridDimx*up->y].before_y = checkNode->y;

			// check adjacency node whether in queue or not
			if ( qSearch(head, up->x, up->y) == 0)
			{
				//printf("push(%d %d)\n", up->x, up->y);
				head = qPush(head, up->x, up->y);
			}
		}
	}

	if (down->x >= 0 && down->x < gridDimx && down->y >= 0 && down->y < gridDimy)
	{
		if ( compareEdgeWeight(checkNode, down, M, routingy, capacity, gridDimx) == 1 )
		{		
			M[down->x + gridDimx*down->y].weight = M[checkNode->x + gridDimx*checkNode->y].weight + countWeight(routingy, down->x, down->y, capacity);
			M[down->x + gridDimx*down->y].length = M[checkNode->x + gridDimx*checkNode->y].length +1;
			M[down->x + gridDimx*down->y].before_x = checkNode->x;
			M[down->x + gridDimx*down->y].before_y = checkNode->y;

			if ( qSearch(head, down->x, down->y) == 0)
			{
				//printf("push(%d %d)\n", down->x, down->y);
				head = qPush(head, down->x, down->y);
			}
		}
	}

	if (right->x >= 0 && right->x < gridDimx && right->y >= 0 && right->y < gridDimy)
	{
		if ( compareEdgeWeight(checkNode, right, M, routingx, capacity, gridDimx) == 1 )
		{
			M[right->x + gridDimx*right->y].weight = M[checkNode->x + gridDimx*checkNode->y].weight + countWeight(routingx, right->x, right->y, capacity);
			M[right->x + gridDimx*right->y].length = M[checkNode->x + gridDimx*checkNode->y].length +1;
			M[right->x + gridDimx*right->y].before_x = checkNode->x;
			M[right->x + gridDimx*right->y].before_y = checkNode->y;

			if ( qSearch(head, right->x, right->y) == 0)
			{
				//printf("push(%d %d)\n", right->x, right->y);
				head = qPush(head, right->x, right->y);
			}
		}
	}

	if (left->x >= 0 && left->x < gridDimx && left->y >= 0 && left->y < gridDimy)
	{	
		if ( compareEdgeWeight(checkNode, left, M, routingx, capacity, gridDimx) == 1 )
		{
			M[left->x + gridDimx*left->y].weight = M[checkNode->x + gridDimx*checkNode->y].weight + countWeight(routingx, left->x, left->y, capacity);
			M[left->x + gridDimx*left->y].length = M[checkNode->x + gridDimx*checkNode->y].length +1;
			M[left->x + gridDimx*left->y].before_x = checkNode->x;
			M[left->x + gridDimx*left->y].before_y = checkNode->y;

			if ( qSearch(head, left->x, left->y) == 0)
			{
				//printf("push(%d %d)\n", left->x, left->y);
				head = qPush(head, left->x, left->y);
			}
		}
	}

	//printf("\n");
	free(up);
	free(down);		
	free(right);
	free(left);

	return head;
}

int compareEdgeWeight(qnode *originNode, qnode *nextNode, wMatrix *M, int **routingMap, int capacity, int gridDimx)
{
	int result = 0;
	int ox = originNode->x;
	int oy = originNode->y;
	int nx = nextNode->x;
	int ny = nextNode->y;

	if ((M[ox + gridDimx*oy].weight + countWeight(routingMap, nx, ny, capacity)) < M[nx + gridDimx*ny].weight )
	{
		result = 1;
	}

	return result;
}

int countWeight(int **routingMap, int x, int y, int capacity)
{
	//printf("nextNode = %d %d\n", x, y);
	int weight = 1;
	int routeNumber = routingMap[x][y];
	//printf("position[%d][%d] route number = %d\n", x, y, routingMap[x][y]);

	if (routeNumber != 0)
	{
		weight = power(2, routeNumber);
		if (routeNumber >= capacity)
		{
			weight = 999;
		}
	}

	return weight;
}

void setLine(wMatrix *M, rMatrix *R, datas *data, int **routingx, int **routingy, int gridDimx)
{
	int last_x, last_y;
	int delta_x, delta_y;
	int x = data->endx;
	int y = data->endy;
	R[x + gridDimx*y].next_x = x;
	R[x + gridDimx*y].next_y = y;

	while( (x != data->startx) || (y != data->starty))
	{
		last_x = M[x + gridDimx*y].before_x;
		last_y = M[x + gridDimx*y].before_y;
		delta_x = last_x - x;
		delta_y = last_y - y;
		if (delta_x == 0)
		{
			routingy[x][y]++;
		}
		else if(delta_y == 0)
		{
			routingx[x][y]++;
		}
		R[last_x + gridDimx*last_y].next_x = x;
		R[last_x + gridDimx*last_y].next_y = y;

		x = last_x;		y = last_y;
	}
}

int power(int val, int exp)
{
	int value = 1;
	for (int i = 1; i <= exp; ++i)
	{
		value = value * val;
	}

	return value;
}




/*************************************************************************************************
*	   		     						queue operation function    		                     *
**************************************************************************************************/
qnode *qPop(qnode *head, qnode *popElement)
{
	if (head == NULL)
	{
		printf("ERROR! queue is empty!\n");
		return head;
	}

	popElement->x = head->x;
	popElement->y = head->y;
	popElement->next = NULL;
	head = head->next;

	return head;
}

qnode *qPush(qnode *head, int pushx, int pushy)
{
	qnode *check = head;
	qnode *newNode = (qnode*)malloc(sizeof(qnode));
	newNode->x = pushx;
	newNode->y = pushy;
	newNode->next = NULL;

	if (check == NULL)
	{
		// queue is empty
		head = newNode;
	}

	else
	{
		while(check->next != NULL)
		{
			check = check->next;
		}
		check->next = newNode;
	}

	return head;
}

// check node already in queue
int qSearch(qnode *head, int checkPosx, int checkPosy)
{
	int find = 0;
	qnode *index = head;

	if (index == NULL)
	{
		return find;
	}

	while(index->next != NULL)
	{
		if (index->x == checkPosx && index->y == checkPosy)
		{
			find = 1;
		}
		index = index->next;
	}
	return find;
}

/*************************************************************************************************
*	   		     					read file and malloc 2d Matrix    		                     *
**************************************************************************************************/
datas *readFile(char const *fileName, int *netNumbers, int *capacity, int *gridDimx, int *gridDimy)
{
	datas *data;
	FILE *fp = fopen(fileName, "r");
	char buf[BUFFER_LENGTH];
	char* token;
	int pointSize = 0;

	int lineCounter = 0, dataCounter = 0;
	while(fgets(buf, BUFFER_LENGTH, fp) != NULL)
	{
		// first line: grid dimention
		if(lineCounter == 0)
		{
			int count = 0;
			token  = strtok(buf, " ");
			while(token != NULL)
			{
				if(count == 1)
					*gridDimx = atoi(token);
				else if (count == 2)
					*gridDimy = atoi(token);

				token = strtok(NULL, " ");
				count++;
			}
			lineCounter++;
		}

		// second line: capacity
		else if (lineCounter == 1)
		{
			int count = 0;
			token  = strtok(buf, " ");
			while(token != NULL)
			{
				if (count == 1)
					*capacity = atoi(token);

				token = strtok(NULL, " ");
				count++;
			}
			lineCounter++;
		}

		// third line: datas numbers
		else if (lineCounter == 2)
		{
			int count = 0;
			token  = strtok(buf, " ");
			while(token != NULL)
			{
				if (count == 2)
					*netNumbers = atoi(token);

				token = strtok(NULL, " ");
				count++;
			}
			data = malloc(*(netNumbers) * sizeof(datas));
			lineCounter++;			
		}

		// point's data
		else
		{
			int count = 0;
			token = strtok(buf, " ");
			while(token != NULL)
			{
				if (count == 1)
					data[dataCounter].startx = atoi(token);
				else if (count == 2)
					data[dataCounter].starty = atoi(token);
				else if (count == 3)
					data[dataCounter].endx = atoi(token);
				else if (count == 4)
					data[dataCounter].endy = atoi(token);

				token = strtok(NULL, " ");
				count++;
			}

			dataCounter++;
		}
	}
	fclose(fp);

	return data;
}

int **mallocMatrix(int row, int col, int initVal)
{
	int **A, *A_row;
	int i, j;

	A = (int**)malloc(row*sizeof(void*));
	A_row = (int*)malloc(row*col*sizeof(int));

	for (i = 0; i < row; ++i, A_row += col)
	{
		A[i] = A_row;
	}

	for (i = 0; i < row; ++i)
	{
		for (j = 0; j < col; ++j)
		{
			A[i][j] = initVal;
		}
	}

	return A;
}