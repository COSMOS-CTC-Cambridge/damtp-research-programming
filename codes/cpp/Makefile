FILES = hello

MPICXX ?= mpicxx

CXXFLAGS := ${CXXFLAGS} -O2 -g
CXXINCLUDE := ${CXXINCLUDE}
LDFLAGS := ${LDFLAGS}
LIBS := ${LIBS}

%.o: %.cpp
	${MPICXX} -c -o $@ ${CXXFLAGS} ${CXXINCLUDE} $<

hello: hello.o
	${MPICXX} -o $@ $< ${LDFLAGS} ${LIBS}

clean:
	rm ${FILES} *.o
