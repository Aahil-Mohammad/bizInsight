#--------Importing Packages-----------------------
import streamlit as st
import numpy as np
import pandas as pd
import os 
import plotly.express as px
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


#---------Page Set up -------------------------------

pd.set_option('display.precision', 2)

st.set_page_config(page_title="BizPulse Insights",page_icon="bizpulse.png",layout="wide")

st.markdown(" ")
st.markdown(" ")
st.image("logo-black.png",width=180)

st.markdown('<style>div.block-container{padding-top:1rem;}</stlye>',unsafe_allow_html=True)
streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Montserrat&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Montserrat', sans-serif;
			}
			</style>
			"""
#-------page elements-------
col, col0 = st.columns([0.7,0.3])
with col:
    fileUpload = st.file_uploader(":file_folder: Upload your csv file", type="csv")
    if fileUpload is not None:
        filename = fileUpload.name
        st.write(filename)
        df = pd.read_csv(filename)
    else:
        os.chdir(r"C:\Users\Aahil\OneDrive\Documents\Projects\StreamLitWebApp")
        df = pd.read_csv("fast_food_orders.csv")




with col0:
    st.markdown('<p style="font-size: 14px; font-family: sans-serif;"> &#128229; Download sample csv file</p>', unsafe_allow_html=True)
    csv_example= ("fast_food_orders.csv")
    st.download_button(label="Download sample file!",data = csv_example,file_name="sampleFile.csv",key="sampleFile")
def download_chart(chartname, key):
    if st.button(f"Download {key} Chart"):
        # Convert the figure to an image
        image = chartname.to_image(format='png')

        # Prompt the user to enter a new file name
        new_file_name = st.text_input('Enter a new file name', f'{key.lower()}_chart.png')

        # Place the download button outside the condition
        st.download_button(label='Download', data=image, file_name=new_file_name, key=f"{key.lower()}_download")

    
df["Order Date"] = pd.to_datetime(df["Order Date"])
col1, col2 = st.columns([0.5,0.5])
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    begDate = pd.to_datetime(st.date_input("Start Date",startDate))

with col2:
    finDate = pd.to_datetime(st.date_input("End Date",endDate))

df = df[(df["Order Date"] >= begDate)&(df["Order Date"] <= finDate)]

st.sidebar.header("Filters")
location = st.sidebar.multiselect("Location",df["Location"].unique())
if not location:
    pass
else :
    df = df[df["Location"].isin(location)]

server = st.sidebar.multiselect("Server",df["Server"].unique())
if not server:
    pass
else :
    df = df[df["Server"].isin(server)]

payment = st.sidebar.multiselect("Payment Method",df["Payment Method"].unique())
if not payment:
    pass
else :
    df = df[df["Payment Method"].isin(payment)]

categorydf = df.groupby(by=["Payment Method"],as_index = False)["Total Sale"].sum()

col3,colb, col4 = st.columns([0.25,0.02,0.2])

with col3:
    st.markdown("<h3 style='text-align: center;'>Sales by Payment Method</h3>", unsafe_allow_html=True)

    barfig = px.bar(categorydf,x="Payment Method",y="Total Sale",color = 'Payment Method',color_discrete_sequence=px.colors.qualitative.Safe,text=['<b>${:,.2f}'.format(x) for x in categorydf["Total Sale"]])
    barfig.update_layout(showlegend=False,xaxis_title=None,yaxis_title=None)
    barfig.update_xaxes(tickfont_family="Arial Black")
    barfig.update_layout(margin=dict(t=0))
    barfig.update_layout(xaxis=dict(showgrid=False),yaxis=dict(showgrid=False))
    barfig.update_yaxes(showticklabels=False)

    st.plotly_chart(barfig,use_container_width=True, height=1)
    download_chart(barfig,'barfig')

with col4:
    st.subheader("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sales by Server") 
        
    filregion = df.groupby(by="Server", as_index=False)["Total Sale"].sum().round(2)
    filregion = filregion.rename(columns={'Total Sale': 'Sales ($)'})
    total_sales = filregion['Sales ($)'].sum()
    percent_sales = (filregion['Sales ($)'] / total_sales) * 100
    filregion['Sales (%)'] = percent_sales
    filregion_sorted = filregion.sort_values(by='Sales ($)', ascending=False)

    # Resetting the index before applying styling
    filregion_sorted.reset_index(drop=True, inplace=True)

    styled_table = (filregion_sorted.style
        .highlight_min(color='orange', axis=0, subset=['Sales ($)', 'Sales (%)'])
        .highlight_max(color='lightgreen', axis=0, subset=['Sales ($)', 'Sales (%)']))

    # Applying CSS for font size
    styled_table.set_table_styles([
        {'selector': 'th', 'props': [('font-size', '50px')]},  # Header font size
        {'selector': 'td', 'props': [('font-size', '14px')]},  # Data font size
    ])

    # Displaying the styled table in Streamlit
    st.write(styled_table)
    
col5, col6 = st.columns([0.7,0.3])
with col5:
    st.subheader("Sales Analysis") 
    df["month_year"] = df["Order Date"].dt.to_period("M")
    linechart = pd.DataFrame(df.groupby(df["month_year"].dt.strftime("%Y-%m"))["Total Sale"].sum()).reset_index()
    linfig = px.line(linechart,x="month_year", y ="Total Sale")
    linfig.update_layout(margin=dict(t=0),xaxis_title=None)
    
    st.plotly_chart(linfig,use_container_width=True)
    download_chart(linfig,"linefig")


mostSold=(df.groupby('Product Name')['Quantity'].sum()).idxmax()
mostSoldMarkdown = f"""
<div style='background-color: #beb4db; padding: 4px; border-radius: 5px; padding-left: 5px;'>
    <h4 style="margin-bottom: -15px; font-size: 20px;">Most Ordered Item &nbsp&#x1F3C6;</h4>
    <p style="text-transform: capitalize; margin: 0; padding-left: 10px; font-size: 18px;"> ➜ {mostSold}</p>
</div>
"""
highestSales = (df.groupby(['Product Name'])['Total Sale'].sum()).idxmax()
highestSalesMarkdown = f"""
<div style='background-color: #9fc8c8; padding: 4px; border-radius: 5px; padding-left: 5px;'>
    <h4 style="margin-bottom: -15px;font-size: 20px;" >High-Earning Item &nbsp &#129297;</h4>
    <p style = "text-transform:capitalize; margin:0px;padding-left: 10px; font-size: 18px;"> ➜ {highestSales}</p>
</div>
"""

bestSalesMonth = ((df["Order Date"].dt.strftime("%B")).value_counts()).idxmax()
bestSalesMonthMarkdown = f"""
<div style='background-color: #A7C7E7; padding: 4px; border-radius: 5px; padding-left: 5px;'>
    <h4 style="margin-bottom: -15px; font-size: 20px;" >Best Sales Month &nbsp &nbsp&#128197;</h4>
    <p style = "text-transform:capitalize; margin:0px;padding-left: 10px; font-size: 18px;"> ➜ {bestSalesMonth}</p>
</div>
"""
topCustomer = df['Customer Name'].value_counts().idxmax()
customerID = df.loc[df['Customer Name'] == topCustomer, 'Customer ID'].iloc[0]
topCustomerMarkdown = f"""
<div style='background-color: #FFA07A; padding: 4px; border-radius: 5px; padding-left: 5px;'>
    <h4 style="margin-bottom: -15px; font-size: 20px;" > Top Customer &nbsp&#128513;</h4>
    <p style = "text-transform:capitalize; margin:0px;padding-left: 10px; font-size: 18px;"> ➜{topCustomer} | ID: {customerID}</p>
</div>
"""

with col6:
    st.subheader("Sales Insights") 
    st.markdown(mostSoldMarkdown, unsafe_allow_html=True)
    st.write(" ")
    st.markdown(highestSalesMarkdown, unsafe_allow_html=True)
    st.write(" ")
    st.markdown(bestSalesMonthMarkdown, unsafe_allow_html=True)
    st.write(" ")
    st.markdown(topCustomerMarkdown, unsafe_allow_html=True)

col7, col8 = st.columns([0.4,0.6])

with col7:
    top_products = df.groupby('Product Name')['Quantity'].sum().nlargest(6).index.tolist()
    df_top6 = df[df['Product Name'].isin(top_products)]

    # Create a pie chart for top 6 products by quantity sold
    piefig = px.pie(df_top6, values='Quantity', names='Product Name', title='Top 6 Products Sold by Quantity')

    # Configure the pie chart to show values inside and remove the legend
    piefig.update_traces(textposition='inside', textinfo='label+percent')
    piefig.update_layout(showlegend=False)
    st.plotly_chart(piefig, use_container_width=True)
    download_chart(piefig,"Pie Chart")

with col8:
    # Group by Product Name and calculate total sale, select top 5 products
    barchart = df.groupby("Product Name")["Total Sale"].sum().reset_index()
    barchart = barchart.sort_values(by="Total Sale", ascending=False).head(5)

    # Create a bar chart with colorful bars and labels inside
    secbarfig = px.bar(barchart, x="Total Sale", y="Product Name", orientation="h", title="                                  Top 5 Products Sold by Sale")
    secbarfig.update_layout(yaxis_title=None)

    # Update the traces to show labels inside and set custom colors
    secbarfig.update_traces(textposition="inside",marker=dict(color=px.colors.qualitative.Vivid))

    # Display the bar chart using Streamlit
    st.plotly_chart(secbarfig, use_container_width=True)
    download_chart(secbarfig,"Bar Chart")
    
