function renderTree(treeData) {
    const treeContainer = document.getElementById("tree-container");
    treeContainer.innerHTML = "";

    const margin = { top: 20, right: 90, bottom: 30, left: 90 },
        width = treeContainer.offsetWidth - margin.left - margin.right,
        height = 800 - margin.top - margin.bottom; // Increased height for better spacing

    const svg = d3
        .select("#tree-container")
        .append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    const zoom = d3.zoom().on("zoom", (event) => {
        svg.attr("transform", event.transform);
    });

    d3.select("#tree-container").select("svg").call(zoom);

    let root = d3.hierarchy(JSON.parse(treeData));
    const treeLayout = d3.tree()
        .size([height, width])
        .nodeSize([50, 350]); // Initial horizontal spacing

    treeLayout.separation((a, b) => (a.parent === b.parent ? 2 : 2.5));

    treeLayout(root);

    // Expand all nodes by default
    root.descendants().forEach((d) => {
        if (d._children) {
            d.children = d._children;
            d._children = null;
        }
    });

    let i = 0;

    function update(source) {
        const nodes = root.descendants().reverse();
        const links = root.links();

        const horizontalSpacing = document.getElementById('horizontal-spacing').value;
        const verticalSpacing = document.getElementById('vertical-spacing').value;

        nodes.forEach(d => {
            d.y = d.depth * horizontalSpacing;
            d.x = d.x * verticalSpacing / 50; // Adjusted vertical spacing
        });

        const node = svg.selectAll('g.node')
            .data(nodes.filter(d => !d.hidden), d => d.id || (d.id = ++i));

        const nodeEnter = node.enter().append('g')
            .attr('class', 'node')
            .attr("transform", d => `translate(${source.y0},${source.x0})`)
            .on('click', click);

        nodeEnter.append('circle')
            .attr('r', 1e-6)
            .style("fill", d => d._children ? "lightsteelblue" : "#fff");

        nodeEnter.append('text')
            .attr("dy", ".35em")
            .attr("x", d => d._children ? -13 : 13)
            .attr("text-anchor", d => d._children ? "end" : "start")
            .text(d => d.data.name)
            .style("font-size", "12px");

        const nodeUpdate = nodeEnter.merge(node);

        nodeUpdate.transition()
            .duration(750)
            .attr("transform", d => `translate(${d.y},${d.x})`);

        nodeUpdate.select('circle')
            .attr('r', 10)
            .style("fill", d => d._children ? "lightsteelblue" : "#fff");

        nodeUpdate.select('text')
            .style("fill-opacity", 1);

        const nodeExit = node.exit().transition()
            .duration(750)
            .attr("transform", d => `translate(${source.y},${source.x})`)
            .remove();

        nodeExit.select('circle')
            .attr('r', 1e-6);

        nodeExit.select('text')
            .style("fill-opacity", 1e-6);

        const link = svg.selectAll('path.link')
            .data(links.filter(d => !d.target.hidden), d => d.target.id);

        const linkEnter = link.enter().insert('path', "g")
            .attr("class", "link")
            .attr('d', d => {
                const o = { x: source.x0, y: source.y0 };
                return diagonal(o, o);
            });

        const linkUpdate = linkEnter.merge(link);

        linkUpdate.transition()
            .duration(750)
            .attr('d', d => diagonal(d.source, d.target));

        const linkExit = link.exit().transition()
            .duration(750)
            .attr('d', d => {
                const o = { x: source.x, y: source.y };
                return diagonal(o, o);
            })
            .remove();

        nodes.forEach(d => {
            d.x0 = d.x;
            d.y0 = d.y;
        });

        function click(event, d) {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d);
            showNodeData(d);
        }
    }

    function diagonal(s, d) {
        return `M ${s.y} ${s.x}
                C ${(s.y + d.y) / 2} ${s.x},
                  ${(s.y + d.y) / 2} ${d.x},
                  ${d.y} ${d.x}`;
    }

    root.x0 = height / 2;
    root.y0 = 0;

    update(root);

    function filterNodes(searchTerm) {
        const searchCriteria = document.getElementById('search-criteria').value;
        const nodes = root.descendants();

        nodes.forEach(d => {
            d.hidden = true;

            if (searchCriteria === 'name' && d.data.name.toLowerCase().includes(searchTerm.toLowerCase())) {
                d.hidden = false;
            } else if (searchCriteria === 'file_analysis' && d.data.file_analysis && d.data.file_analysis.toLowerCase().includes(searchTerm.toLowerCase())) {
                d.hidden = false;
            }

            if (!d.hidden) {
                let ancestor = d;
                while (ancestor) {
                    ancestor.hidden = false;
                    ancestor = ancestor.parent;
                }
            }
        });

        update(root);
    }

    document.getElementById('search-bar').addEventListener('input', function () {
        filterNodes(this.value);
    });

    document.getElementById('zoom-in').addEventListener('click', function () {
        zoom.scaleBy(d3.select("#tree-container").select("svg"), 1.2);
    });

    document.getElementById('zoom-out').addEventListener('click', function () {
        zoom.scaleBy(d3.select("#tree-container").select("svg"), 0.8);
    });

    document.getElementById('horizontal-spacing').addEventListener('input', function () {
        update(root);
    });

    document.getElementById('vertical-spacing').addEventListener('input', function () {
        update(root);
    });
}

function showNodeData(d) {
    const nodeData = { ...d.data };
    delete nodeData.children;

    const keyMapping = {
        name: 'File Name',
        file_analysis: 'File Overview'
    };

    let detailsHtml = '';
    for (const [key, value] of Object.entries(nodeData)) {
        const displayKey = keyMapping[key] || key;
        detailsHtml += `<div><strong>${displayKey}:</strong> ${value}</div>`;
    }

    document.getElementById('node-data-content').innerHTML = detailsHtml;
}

$("#treeModal").on("shown.bs.modal", function () {
    renderTree(window.treeData);
});
