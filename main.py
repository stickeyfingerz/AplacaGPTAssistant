from display import *


def inject_custom_css():
    custom_css = """
    <style>
/* Overall background, text color, and font */
body {
    background-color: #0A0A0A; /* Dark background */
    color: #f9e297; /* Gold text color */
    font-family: 'Papyrus', Fantasy; /* Consistent font */
}

/* Header customization */
h1 {
    color: #f9e297; /* Gold color for header */
}

/* Sidebar customization */
.stSidebar {
    background-color: #787878; /* Darker sidebar background */
    color: #f0f0f0; /* Light text in sidebar */
}

/* Button customization */
.stButton > button {
    background-color: #b4b4b4; /* Gold background */
    color: #f0f0f0; /* Dark text */
    transition: background-color 0.3s; /* Smooth transition for hover */
}
.stButton > button:hover {
    background-color: #FFD700; /* Change color on hover */
}

/* Link customization */
a {
    color: #FFD700; /* Gold color for links */
    text-decoration: none; /* No underline */
}
a:hover {
    text-decoration: underline; /* Underline on hover */
}

/* Responsive image class */
        .responsive-image {
            max-width: 50%; /* Maximum width of the image is 100% of the container */
            height: auto; /* Image height adjusts automatically */
            display: block; /* Block display to allow margin auto to be effective */
            margin-left: auto; /* Center the image */
            margin-right: auto; /* Center the image */
        }

/* Mobile-friendly adjustments */
    @media (max-width: 768px) { /* Adjusting for more common mobile screen widths */
        .stButton > button {
            width: 100%; /* Full width buttons */
            padding: 12px 24px; /* Larger tap area */
            font-size: 16px; /* Legible font size */
            margin-bottom: 10px; /* Space between buttons */
        }

        h1, h2, h3, h4, h5, h6 {
            font-size: 5vw; /* Responsive font size */
        }

        /* Sidebar font size adjustment for readability */
        .stSidebar .css-1d391kg {
            font-size: 14px;
        }
    }

    /* Additional custom styles */
    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)


def main():
    page = (['AI'])
    tab1, tab2, tab3, = st.tabs(['Home', 'Account Data', 'Coder'])
    if page:
        display_AI()
    # Display the selected page
    with tab1:
        display_home_page()
    with tab2:
        display_account_data()
    with tab3:
        display_coder()


if __name__ == "__main__":
    main()
