message(STATUS "running 'CPP/testsuite' makelists...")

# Include all test files
# If a upper level CMAKE file includes this (to use the same project), it should set its source files to SOURCE_FILES
file(GLOB TESTSUITE_SOURCE_FILES ${CMAKE_CURRENT_LIST_DIR}/*.cpp)
file(GLOB TESTSUITE_HEADER_FILES ${CMAKE_CURRENT_LIST_DIR}/*.h)

# Include the minute testing framework header
set(MINUNIT_FILES
    ${CMAKE_CURRENT_LIST_DIR}/minunit/minunit.h
    ${CMAKE_CURRENT_LIST_DIR}/minunit/minunit.cpp
    )

set(SOURCE_FILES
	${SOURCE_FILES}
	${TESTSUITE_SOURCE_FILES}
	${TESTSUITE_HEADER_FILES}
	${MINUNIT_FILES}
	)
