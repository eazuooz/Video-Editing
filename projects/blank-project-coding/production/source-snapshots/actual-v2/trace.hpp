#pragma once
#include <iostream>
#include <string>
#include <sstream>
struct Node { int value; Node* next; };
inline std::string address(Node* p) { if(!p) return "nullptr"; std::ostringstream o; o<<static_cast<void*>(p); return o.str(); }
// A small, explicit instrumentation debugger: values come from this compiled
// process, and Enter resumes it. No prerecorded or fabricated pointer values.
inline void inspect(const char* label, Node* head, Node* current=nullptr) {
  std::cout<<"{\"type\":\"breakpoint\",\"label\":\""<<label<<"\",\"head\":\""<<address(head)<<"\",\"current\":\""<<address(current)<<"\",\"nodes\":[";
  bool comma=false; int guard=0;
  for(Node* n=head;n && guard++<16;n=n->next){if(comma)std::cout<<",";comma=true;std::cout<<"{\"address\":\""<<address(n)<<"\",\"value\":"<<n->value<<",\"next\":\""<<address(n->next)<<"\"}";}
  std::cout<<"]}"<<std::endl;
  std::string command; std::getline(std::cin,command);
}
inline void printList(Node* head) {std::cout<<"values: ";for(Node* n=head;n;n=n->next)std::cout<<n->value<<" ";std::cout<<"| end: nullptr"<<std::endl;}
inline void destroy(Node*& head) {while(head){Node* old=head;head=head->next;delete old;}}
