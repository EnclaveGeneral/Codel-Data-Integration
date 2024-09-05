import pandas as pd
import io
import traceback
import csv

def bom_graph(files):
    try:
        bom_details_list = files['bom_details_list']
        bom_parents_list = files['bom_parents_list']

        print("Reading Excel files...")
        details = pd.read_excel(bom_details_list, skiprows=7).dropna(how="all")
        parents = pd.read_excel(bom_parents_list, skiprows=6).dropna(how="all")

        print("Details columns:", details.columns)
        print("Parents columns:", parents.columns)
        print(f"Details shape: {details.shape}, Parents shape: {parents.shape}")

        print("Creating BOM ID set...")
        ids = set()
        for bom in details["BOM ID"]:
            try:
                ids.add(int(bom))
            except ValueError:
                print(f"Warning: Non-integer BOM ID found: {bom}")

        seen = set()
        adj = {}
        desc = {}

        print("Processing details...")
        for i in range(len(details)):
            try:
                cur = int(details.iloc[i]["BOM ID"])
                nxt = details.iloc[i]["Next Bom"]
                if pd.notna(nxt):
                    nxt = int(nxt)
                else:
                    continue

                if cur not in desc:
                    desc[cur] = str(details.iloc[i]["Description"]).replace('"', '').replace(",", "")
                if nxt and nxt in ids:
                    if cur not in seen:
                        seen.add(cur)
                    if nxt not in seen:
                        seen.add(nxt)
                    if cur not in adj:
                        adj[cur] = set()
                    adj[cur].add(nxt)
            except Exception as e:
                print(f"Error processing details row {i}: {e}")

        print("Processing parents...")
        for i in range(len(parents)):
            try:
                cur = int(parents.iloc[i]["BOM ID"])
                nxt = parents.iloc[i]["Next"]
                if pd.notna(nxt):
                    nxt = int(nxt)
                else:
                    continue

                if cur not in desc:
                    desc[cur] = str(parents.iloc[i]["Description.1"]).replace('"', '').replace(",", "")
                if nxt and nxt in ids:
                    if cur not in seen:
                        seen.add(cur)
                    if nxt not in seen:
                        seen.add(nxt)
                    if cur not in adj:
                        adj[cur] = set()
                    adj[cur].add(nxt)
            except Exception as e:
                print(f"Error processing parents row {i}: {e}")

        print("Writing output...")
        output = io.BytesIO()
        text_stream = io.TextIOWrapper(output, encoding='utf-8', newline='')
        csv_writer = csv.writer(text_stream)
        csv_writer.writerow(["BOM ID", "Description", "Next BOM ID", "Description"])

        for bom in adj:
            for nxt in adj[bom]:
                csv_writer.writerow([bom, desc.get(bom, 'N/A'), nxt, desc.get(nxt, 'N/A')])

        text_stream.detach()  # Prevent closing of the underlying BytesIO
        output.seek(0)
        print(f"Output size: {output.getbuffer().nbytes} bytes")
        print("Processing completed successfully.")
        return output
    except Exception as e:
        print(f"Error in process_method2: {str(e)}")
        print(traceback.format_exc())
        raise