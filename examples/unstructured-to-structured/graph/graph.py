from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph


from graph.consts import CLASSIFY_DOCUMENTS, INVOICE_DATA_CAPTURE
from graph.nodes.classify_documents import classify_documents
from graph.nodes.invoice_data_capture import invoice_data_capture
from graph.state import GraphState


load_dotenv()


# Initialize the graph
workflow = StateGraph(GraphState)


workflow.add_node(CLASSIFY_DOCUMENTS, classify_documents)
workflow.add_node(INVOICE_DATA_CAPTURE, invoice_data_capture)

# Entry point
workflow.set_entry_point(CLASSIFY_DOCUMENTS)

workflow.add_edge(CLASSIFY_DOCUMENTS, INVOICE_DATA_CAPTURE)


workflow.add_edge(INVOICE_DATA_CAPTURE, END)


app = workflow.compile()