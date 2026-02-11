#!/usr/bin/env python3
"""
Generate HTML report from benchmark results
"""

import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def load_results(filepath='results/benchmark_results.json'):
    """Load benchmark results from JSON"""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_crud_comparison_chart(results):
    """Create bar chart comparing CRUD operations"""
    databases = []
    insert_times = []
    select_times = []
    update_times = []
    delete_times = []
    
    for db_name, db_data in results['databases'].items():
        if 'error' in db_data:
            continue
        
        crud = db_data.get('crud', {})
        databases.append(db_name.upper())
        insert_times.append(crud.get('insert_customers', 0) * 1000)
        select_times.append(crud.get('select_simple', 0) * 1000)
        update_times.append(crud.get('update_batch', 0) * 1000)
        delete_times.append(crud.get('delete_batch', 0) * 1000)
    
    fig = go.Figure(data=[
        go.Bar(name='Insert (1000 rows)', x=databases, y=insert_times),
        go.Bar(name='Select (simple)', x=databases, y=select_times),
        go.Bar(name='Update (500 rows)', x=databases, y=update_times),
        go.Bar(name='Delete (100 rows)', x=databases, y=delete_times)
    ])
    
    fig.update_layout(
        title='CRUD Operations Performance Comparison',
        xaxis_title='Database',
        yaxis_title='Time (milliseconds)',
        barmode='group',
        template='plotly_white',
        height=500
    )
    
    return fig.to_html(include_plotlyjs='cdn', div_id='crud-chart')

def create_index_impact_chart(results):
    """Create chart showing index performance impact"""
    databases = []
    without_index = []
    with_index = []
    
    for db_name, db_data in results['databases'].items():
        if 'error' in db_data:
            continue
        
        indexing = db_data.get('indexing', {})
        if indexing:
            databases.append(db_name.upper())
            without_index.append(indexing.get('without_index', 0) * 1000)
            with_index.append(indexing.get('with_index', 0) * 1000)
    
    fig = go.Figure(data=[
        go.Bar(name='Without Index', x=databases, y=without_index),
        go.Bar(name='With Index', x=databases, y=with_index)
    ])
    
    fig.update_layout(
        title='Index Performance Impact',
        xaxis_title='Database',
        yaxis_title='Query Time (milliseconds)',
        barmode='group',
        template='plotly_white',
        height=400
    )
    
    return fig.to_html(include_plotlyjs='cdn', div_id='index-chart')

def generate_html_report(results):
    """Generate complete HTML report"""
    
    crud_chart = create_crud_comparison_chart(results)
    index_chart = create_index_impact_chart(results)
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Database Benchmark Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }}
            
            header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            
            h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                opacity: 0.9;
                font-size: 1.1em;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .section {{
                margin-bottom: 40px;
            }}
            
            h2 {{
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.8em;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            
            .stat-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            
            .stat-card h3 {{
                color: #333;
                font-size: 1.2em;
                margin-bottom: 10px;
            }}
            
            .stat-value {{
                font-size: 2em;
                color: #667eea;
                font-weight: bold;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            
            th {{
                background: #667eea;
                color: white;
                font-weight: 600;
            }}
            
            tr:hover {{
                background: #f5f5f5;
            }}
            
            .chart-container {{
                margin: 30px 0;
            }}
            
            footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
            }}
            
            .timestamp {{
                color: #999;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Database Performance Benchmark</h1>
                <p class="subtitle">PostgreSQL vs MySQL vs MongoDB</p>
                <p class="timestamp">Generated: {results['timestamp']}</p>
            </header>
            
            <div class="content">
                <div class="section">
                    <h2>Overview</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>Dataset Size</h3>
                            <div class="stat-value">{results['config']['dataset_size']:,}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Databases Tested</h3>
                            <div class="stat-value">{len(results['databases'])}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Test Iterations</h3>
                            <div class="stat-value">{results['config']['iterations']}</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>CRUD Performance Comparison</h2>
                    <div class="chart-container">
                        {crud_chart}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Index Performance Impact</h2>
                    <div class="chart-container">
                        {index_chart}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Detailed Results</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Database</th>
                                <th>Insert (ms)</th>
                                <th>Select (ms)</th>
                                <th>Update (ms)</th>
                                <th>Delete (ms)</th>
                                <th>Index Improvement</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Add table rows
    for db_name, db_data in results['databases'].items():
        if 'error' in db_data:
            continue
        
        crud = db_data.get('crud', {})
        indexing = db_data.get('indexing', {})
        
        html_template += f"""
                            <tr>
                                <td><strong>{db_name.upper()}</strong></td>
                                <td>{crud.get('insert_customers', 0)*1000:.2f}</td>
                                <td>{crud.get('select_simple', 0)*1000:.2f}</td>
                                <td>{crud.get('update_batch', 0)*1000:.2f}</td>
                                <td>{crud.get('delete_batch', 0)*1000:.2f}</td>
                                <td>{indexing.get('improvement_percent', 0):.1f}%</td>
                            </tr>
        """
    
    html_template += """
                        </tbody>
                    </table>
                </div>
            </div>
            
            <footer>
                <p>Generated by Database Benchmark Tool | <a href="https://github.com/yourusername/db-benchmark-tool">GitHub</a></p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html_template

def main():
    # Load results
    results = load_results()
    
    # Generate HTML
    html_content = generate_html_report(results)
    
    # Save report
    os.makedirs('reports', exist_ok=True)
    output_path = 'reports/index.html'
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"✓ HTML report generated: {output_path}")
    print(f"  Open file://{os.path.abspath(output_path)} in your browser")

if __name__ == '__main__':
    main()
