from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph


from graph.consts import INFERENCE_SCHEMA, INVOICE_DATA_CAPTURE, GENERATE_CSV
from graph.nodes.inference_schema import inference_schema
from graph.nodes.invoice_data_capture import invoice_data_capture
from graph.nodes.generate_csv import generate_csv
from graph.state import GraphState


load_dotenv()


# Initialize the graph
workflow = StateGraph(GraphState)


workflow.add_node(INFERENCE_SCHEMA, inference_schema)
workflow.add_node(INVOICE_DATA_CAPTURE, invoice_data_capture)
workflow.add_node(GENERATE_CSV, generate_csv)

# Entry point

workflow.set_entry_point(INFERENCE_SCHEMA)

workflow.add_edge(INFERENCE_SCHEMA, INVOICE_DATA_CAPTURE)

workflow.add_edge(INVOICE_DATA_CAPTURE, GENERATE_CSV)

workflow.add_edge(GENERATE_CSV, END)


app = workflow.compile()

# app.get_graph().draw_mermaid_png(output_file_path="graph.png")
