import streamlit as st
import plotly.graph_objects as go
import ifcopenshell
import numpy as np

def extract_faces(ifc_file):
    """
    Extracts faces and their coordinates from an IFC file, with added error handling.
    """
    faces_with_coords = []
    for ifc_product in ifc_file.by_type("IfcProduct"):
        representation = ifc_product.Representation
        if representation is not None:
            for representation_item in representation.Representations:
                if representation_item.RepresentationType == 'Tessellation':
                    try:
                        # Attempt to create a geometric shape from the representation item
                        geometry = ifcopenshell.geom.create_shape(representation_item)
                        verts = np.array(geometry.verts).reshape((-1, 3))
                        indices = np.array(geometry.edges).reshape((-1, 3))
                        for i in indices:
                            face = [verts[index] for index in i]
                            faces_with_coords.append(face)
                    except Exception as e:
                        # Log or display the error for debugging
                        st.error(f"Error processing geometry for {ifc_product}: {e}")
                        continue
    return faces_with_coords

def plot_3d_model(faces_with_coords):
    """
    Plots a 3D model from extracted faces using Plotly.
    """
    fig = go.Figure()

    for face in faces_with_coords:
        x, y, z = zip(*face)
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            color='blue',
            opacity=0.5
        ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(showbackground=False),
            yaxis=dict(showbackground=False),
            zaxis=dict(showbackground=False)
        )
    )
    return fig

def main():
    st.title('IFC File 3D Viewer')

    uploaded_file = st.file_uploader("Upload an IFC file", type=['ifc'])
    if uploaded_file is not None:
        ifc_file = ifcopenshell.file.from_string(uploaded_file.getvalue().decode("utf-8"))
        faces_with_coords = extract_faces(ifc_file)
        if faces_with_coords:
            fig = plot_3d_model(faces_with_coords)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No faces could be extracted from the uploaded IFC file. Please check the file or try another.")

if __name__ == "__main__":
    main()
