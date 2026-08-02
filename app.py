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

    st.markdown("**Optional limits** (leave at 0 to use the full image)")
    xlim_input = st.number_input("xlim (pixels)", min_value=0, value=0, step=1)
    ylim_input = st.number_input("ylim (pixels)", min_value=0, value=0, step=1)

    use_wcs_xlim = st.checkbox("Use wcs_xlim instead")
    use_wcs_ylim = st.checkbox("Use wcs_ylim instead")

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

    xlim = int(xlim_input) if xlim_input > 0 else None
    ylim = int(ylim_input) if ylim_input > 0 else None
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
            )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Image with cut line")
            st.pyplot(fig1)
        with col2:
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
