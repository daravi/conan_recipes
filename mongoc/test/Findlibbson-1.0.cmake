find_path(BSON_INCLUDE_DIR NAMES bson.h PATHS ${CONAN_INCLUDE_DIRS_MONGO-C-DRIVER})

set(BSON_FOUND TRUE)
set(BSON_INCLUDE_DIRS ${BSON_INCLUDE_DIR})
set(BSON_LIBRARIES ${CONAN_LIBS})
mark_as_advanced(BSON_LIBRARY BSON_INCLUDE_DIR)
