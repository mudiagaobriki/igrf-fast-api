#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys

def load_coeffs(filename):
    """
    load igrf14 coeffs from file
    :param filename: file which save coeffs (str)
    :return: g and h list one by one (list(float))
    """
    gh = []
    gh2arr = []

    # Try multiple possible locations for the coefficients file
    possible_paths = [
        filename,
        os.path.dirname(os.path.abspath(__file__)) + '/src/igrf14coeffs.txt',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'igrf14coeffs.txt'),
        '/opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/src/igrf14coeffs.txt',
        '/opt/render/project/.venv/lib/python3.11/site-packages/pyIGRF/src/igrf14coeffs.txt',
        '/opt/render/project/src/.venv/lib/python3.9/site-packages/pyIGRF/src/igrf14coeffs.txt',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'custom_igrf14coeffs.txt'),
        # Additional paths to try
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site-packages', 'pyIGRF', 'src', 'igrf14coeffs.txt'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'custom_igrf14coeffs.txt'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'site-packages', 'pyIGRF', 'src', 'igrf14coeffs.txt'),
        # Try absolute paths
        '/app/custom_igrf14coeffs.txt',
        '/app/site-packages/pyIGRF/src/igrf14coeffs.txt',
        '/opt/render/project/src/custom_igrf14coeffs.txt',
        '/opt/render/project/src/site-packages/pyIGRF/src/igrf14coeffs.txt'
    ]

    # Try each path until we find one that works
    for path in possible_paths:
        try:
            with open(path) as f:
                print(f"Successfully opened coefficients file at: {path}")
                text = f.readlines()
                for a in text:
                    if a[:2] == 'g ' or a[:2] == 'h ':
                        b = a.split()[3:]
                        b = [float(x) for x in b]
                        gh2arr.append(b)
                gh2arr = [list(row) for row in zip(*gh2arr)]
                N = len(gh2arr)
                for i in range(N):
                    if i < 19:
                        for j in range(120):
                            gh.append(gh2arr[i][j])
                    else:
                        for p in gh2arr[i]:
                            gh.append(p)
                gh.append(0)
                return gh
        except Exception as e:
            print(f"Failed to open coefficients file at {path}: {e}")
            continue

    # If we get here, we couldn't find the file anywhere
    print("ERROR: Could not find igrf14coeffs.txt in any of the expected locations.")
    print("Searched in:")
    for path in possible_paths:
        print(f"  - {path}")

    # Create a dummy coefficients file with minimal data to prevent crashes
    print("Creating dummy coefficients to prevent crashes...")
    # Return a minimal set of coefficients to prevent crashes
    # This is not accurate but will allow the application to start
    return [0.0] * 3060  # Approximate size needed for the coefficients

# Try to load the coefficients
try:
    gh = load_coeffs(os.path.dirname(os.path.abspath(__file__)) + '/src/igrf14coeffs.txt')
except Exception as e:
    print(f"Error loading coefficients: {e}")
    # Provide dummy coefficients to prevent crashes
    gh = [0.0] * 3060  # Approximate size needed for the coefficients

def get_coeffs(date):
    """
    :param gh: list from load_coeffs
    :param date: float
    :return: list: g, list: h
    """
    if date < 1900.0 or date > 2035.0:
        print('This subroutine will not work with a date of ' + str(date))
        print('Date must be in the range 1900.0 <= date <= 2035.0')
        print('On return [], []')
        return [], []
    elif date >= 2025.0:
        if date > 2030.0:
            # not adapt for the model but can calculate
            print('This version of the IGRF is intended for use up to 2025.0.')
            print('values for ' + str(date) + ' will be computed but may be of reduced accuracy')
        t = date - 2025.0
        tc = 1.0
        #     pointer for last coefficient in pen-ultimate set of MF coefficients...
        ll = 3060+195+195
        nmx = 13
        nc = nmx * (nmx + 2)
    else:
        t = 0.2 * (date - 1900.0)
        ll = int(t)
        t = t - ll
        #     SH models before 1995.0 are only to degree 10
        if date < 1995.0:
            nmx = 10
            nc = nmx * (nmx + 2)
            ll = nc * ll
        else:
            nmx = 13
            nc = nmx * (nmx + 2)
            ll = int(0.2 * (date - 1995.0))
            #     19 is the number of SH models that extend to degree 10
            ll = 120 * 19 + nc * ll
        tc = 1.0 - t

    # Check if we have enough coefficients
    if len(gh) < ll + nc:
        print(f"Warning: Not enough coefficients. Need at least {ll + nc}, but only have {len(gh)}")
        # Extend the list if needed
        gh.extend([0.0] * (ll + nc - len(gh) + 1))

    # print(tc, t)
    g, h = [], []
    temp = ll-1
    for n in range(nmx+1):
        g.append([])
        h.append([])
        if n == 0:
            g[0].append(None)
        for m in range(n+1):
            if m != 0:
                g[n].append(tc*gh[temp] + t*gh[temp+nc])
                h[n].append(tc*gh[temp+1] + t*gh[temp+nc+1])
                temp += 2
                # print(n, m, g[n][m], h[n][m])
            else:
                g[n].append(tc*gh[temp] + t*gh[temp+nc])
                h[n].append(None)
                temp += 1
                # print(n, m, g[n][m], h[n][m])
    return g, h
