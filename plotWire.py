# Plots the distribution in a WikiSim or WiRe file
# run as: wire2gwikimatch.py -i <inputfile> -o <outputfile>
import sys,argparse
import time

import plotly.express as px
import plotly.graph_objects as go


def read_arguments():
    """
    Read arguments from the command line
    :return: (outputdirectory, language)
    """

    parser = argparse.ArgumentParser(description='Plot a distribution of the relatedness in wire and wikisim files.')
    parser.add_argument('-r', '--wire', help='The WiRe tsv file', required=True)
    parser.add_argument('-s', '--wikisim', help='The wikisim file', required=True)
    parser.add_argument('-o', '--output', help='The output file with the diagram', required=True)

    args = vars(parser.parse_args())

    return (args["wire"], args["wikisim"], args["output"])


def create_count_dictionary( file):
    """
    Create a list of the number of occurrences
    :param file: The input TSV file
    :return: a dictionary containing the value as a key and the number of items with this value as a value
             the key is a value between 0 and 10
    """

    vals = {}
    for i in range(0, 11):
        vals[str(i)] = 0

    with open( file, "r") as f:
        for line in f.readlines():
            fields = line.strip().split("\t")
            vals[fields[0]] += 1

    return vals


def visualize( wire, wikisim, imagefile):
    colors = ["rgb(116,0,48)","rgb(237,92,139)","rgb(38,139,210)","rgb(108,113,196)","rgb(211,54,130)","rgb(220,50,47)","rgb(203,75,22)","rgb(181,137,0)"]

    wiredata = create_count_dictionary( wire)
    wikisimdata = create_count_dictionary( wikisim)

    plot = go.Figure(data=[go.Line(
            name="WiRe",
            x = list(wiredata.keys()),
            y = list(wiredata.values()),
            marker_color=colors[0]
    ),
        go.Line(
            name="WikiSim",
            x = list(wikisimdata.keys()),
            y = list(wikisimdata.values()),
            marker_color=colors[1]
    )
    ])

    plot.update_layout(
        {"xaxis": {
            "title": "Validity of the relation"
        },
        "yaxis": {
            "title": "Number of relations"
        }
    })

    ## Workaround to remove error message from pdf
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    fig.write_image(imagefile, format="pdf")
    time.sleep(2)

    plot.write_image(imagefile)


# Main part of the script
if __name__ == '__main__':
    (wire, wikisim, output) = read_arguments()

    visualize(wire, wikisim, output)

    print("done")