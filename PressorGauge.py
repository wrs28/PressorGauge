import streamlit as st
import numpy as np
import pandas as pd
from joblib import load



clf, X_test, y_test = load("model.joblib")


# Add a selectbox to the sidebar:
index = st.sidebar.selectbox(
    'How would you like to be contacted?',
    range(len(y_test))
)


"""
# VentSure
"""


X_test[index]




X_test0 = float(st.text_input("label goes here", X_test[index][0]))
X_test1 = float(st.text_input("label goes here", X_test[index][1]))
X_test2 = float(st.text_input("label goes here", X_test[index][2]))
X_test3 = float(st.text_input("label goes here", X_test[index][3]))

X_test = np.array([[X_test0,X_test1,X_test2,X_test3],])
a = clf.predict(X_test)
a[0]

y_test[index]

# progress_bar = st.progress(0)
# status_text = st.empty()
# chart = st.line_chart(np.random.randn(10, 2))

# for i in range(100):
#     # Update progress bar.
#     progress_bar.progress(i)
#
#     new_rows = np.random.randn(10, 2)
#
#     # Update status text.
#     status_text.text(
#         'The latest random number is: %s' % new_rows[-1, 1])
#
#     # Append data to the chart.
#     chart.add_rows(new_rows)
#
#     # Pretend we're doing some computation that takes time.
#     time.sleep(0.1)
#
# status_text.text('Done!')
# st.balloons()



# Add a slider to the sidebar:
# add_slider = st.sidebar.slider(
    # 'Select a range of values',
    # 0.0, 100.0, (25.0, 75.0)
# )

# add_slider[0]




# st.write("# hello")
# st.write("* this is a *bullet* point")

# st.write("Here's our first attempt at using data to create a table:")
# df = pd.DataFrame({
    # "first column": [1,2,3,4],
    # "second column": [10,20,30,40]
# })
# st.write(df)
# st.dataframe(df)
# st.table(df)

# """
# # My first app
# Here's our first attempt at using data to create a table:
# """

# df

# chart_data = pd.DataFrame(
     # np.random.randn(20, 3),
     # columns=['a', 'b', 'c'])

# st.line_chart(chart_data)

# map_data = pd.DataFrame(
    # np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    # columns=['lat', 'lon'])

# st.map(map_data)

# if st.checkbox('Show dataframe'):
    # chart_data = pd.DataFrame(
       # np.random.randn(20, 3),
       # columns=['a', 'b', 'c'])

    # st.line_chart(chart_data)

# option1 = st.selectbox(
    # 'Which number do you like best?',
     # df['first column'])

# 'You selected: ', option1


# option2 = st.sidebar.selectbox(
    # 'Which number do you like best?',
     # df['second column'])

# 'You selected:', option2

#
# # Get some data.
# data = np.random.randn(10, 2)
#
# # Show the data as a chart.
# chart = st.line_chart(data)
#
# # Wait 1 second, so the change is clearer.
# time.sleep(5)
#
# # Grab some more data.
# data2 = np.random.randn(10, 2)
#
# # Append the new data to the existing chart.
# chart.add_rows(data2)

#
# 'Starting a long computation...'
#
# # Add a placeholder
# latest_iteration = st.empty()
# bar = st.progress(0)
#
# for i in range(100):
#   # Update the progress bar with each iteration.
#   latest_iteration.text(f'Iteration {i+1}')
#   bar.progress(i + 1)
#   time.sleep(0.1)
#
# '...and now we\'re done!'
