#include <cstdint>
#include <iostream>
#include <vector>
#include <bsoncxx/json.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include <mongocxx/stdx.hpp>
#include <mongocxx/uri.hpp>
#include <bsoncxx/builder/stream/document.hpp>

using bsoncxx::builder::stream::close_array;
using bsoncxx::builder::stream::close_document;
using bsoncxx::builder::stream::document;
using bsoncxx::builder::stream::finalize;
using bsoncxx::builder::stream::open_array;
using bsoncxx::builder::stream::open_document;

int main()
{

	mongocxx::instance instance {};	 // This should be done only once.
	mongocxx::uri uri("mongodb://localhost:27017");
	mongocxx::client client(uri);

	mongocxx::database db = client["mydb13"];
	mongocxx::collection coll = db["mycol3"];

	auto builder = bsoncxx::builder::stream::document {};
	bsoncxx::document::value doc_value = 
		builder 
			<< "name" << "MongoDB"
			<< "type" << "database"
			<< "count" << 1 
			<< "versions" 
				<< bsoncxx::builder::stream::open_array 
					<< "v3.2" << "v3.0" << "v2.6" 
				<< close_array 
			<< "info" 
				<< bsoncxx::builder::stream::open_document 
					<< "x" << 203
					<< "y" << 102 
				<< bsoncxx::builder::stream::close_document 
		<< bsoncxx::builder::stream::finalize;
	
	bsoncxx::document::view view = doc_value.view();


    std::cout << "Bincrafters2\n";
    return EXIT_SUCCESS;
}
