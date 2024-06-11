#
# ©2015 Symbol Technologies LLC. All rights reserved.
#

CC = g++
CXXFLAGS = -Wall -g -I/usr/include/zebra-scanner -I./include/
LFLAGS = -L/usr/lib/zebra-scanner/corescanner -I./include/
LIBS = -lcs-client -lcs-common
SRCS = ./src/main.cpp ./src/EventListener.cpp
OBJS = $(SRCS:.cpp=.o)
MAIN = ./bin/runScanner

.PHONY: depend clean

all:	$(MAIN)

$(MAIN): $(OBJS)
		$(CC) $(CXXFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)

.c.o:
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

.cpp.o:
	$(CC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	$(RM) ./src/*.o *~ $(MAIN)
	
depend: $(SRC)
	makedepend $(INCLUDES) $^
