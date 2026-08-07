import tempfile
import os

import streamlit as st
import numpy as np
import pandas as pd

from line_profile import make_line

st.set_page_config(page_title="FITS Radial Intensity Profile", layout="wide")

st.title("🔭 FITS Radial Intensity Profile")
st.write(
    "Upload a FITS image, choose a position angle for the cut line, and "
    "extract a radial intensity profile from the brightest pixel outward."
)

with st.sidebar:
    st.header("Inputs")

    uploaded_file = st.file_uploader("FITS file", type=["fits", "fit", "fts"])

    angle = st.number_input(
        "Angle (degrees)",
        min_value=-180.0,
        max_value=180.0,
        value=0.0,
        step=1.0,
        help="Position angle of the cut line.",
    )

    st.markdown("**Optional line limits** (leave at 0 to use the full image)")
    line_limit_x_axis = st.number_input("xlim (pixels)", min_value=0, value=0, step=1)
    line_limit_y_axis = st.number_input("ylim (pixels)", min_value=0, value=0, step=1)
    use_wcs_xlim = st.checkbox("Use wcs_xlim instead")
    use_wcs_ylim = st.checkbox("Use wcs_ylim instead")

    st.markdown("**Optional image crop** (leave at 0 to use the full image)")
    image_limit_x = st.number_input("image_limit_x", min_value=0, value=0, step=1)
    image_limit_y = st.number_input("image_limit_y", min_value=0, value=0, step=1)

    run_button = st.button("Run", type="primary")

if run_button:
    if uploaded_file is None:
        st.error("Please upload a FITS file first.")
        st.stop()

    # make_line requires a string file path (per its own type check), so we
    # write the uploaded bytes to a temporary file on disk.
    suffix = os.path.splitext(uploaded_file.name)[1] or ".fits"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    xlim = int(line_limit_x_axis) if line_limit_x_axis > 0 else None
    ylim = int(line_limit_y_axis) if line_limit_y_axis > 0 else None
    image_limit_x_para = int(image_limit_x) if image_limit_x > 0 else None
    image_limit_y_para = int(image_limit_y) if image_limit_y > 0 else None
    wcs_xlim = "yes" if use_wcs_xlim else None
    wcs_ylim = "yes" if use_wcs_ylim else None

    try:
        with st.spinner("Extracting profile..."):
            fig1, fig2, dist, vals_on_line = make_line(
                tmp_path,
                angle,
                xlim=xlim,
                ylim=ylim,
                wcs_xlim=wcs_xlim,
                wcs_ylim=wcs_ylim,
                image_limit_x=image_limit_x_para,
                image_limit_y=image_limit_y_para,
            )

        st.subheader("Image with cut line")
        st.pyplot(fig1)

        st.subheader("Radial intensity profile")
        st.pyplot(fig2)

        df = pd.DataFrame({"distance_px": dist, "intensity": vals_on_line})
        st.subheader("Profile data")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download profile as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="radial_profile.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Something went wrong: {e}")

    finally:
        os.remove(tmp_path)

else:
    st.info("Upload a FITS file and click **Run** to generate the profile.")