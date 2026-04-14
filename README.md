# 高可靠性金融數據採集與異常監控系統 (Fin-Data ETL & Monitoring)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Container-Docker-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

##  專案概述
本專案是一個基於 **微服務架構** 的分散式金融數據採集系統。設計初衷是為了解決高頻採集時常見的 **反爬蟲限制 (429 Too Many Requests)**、**數據一致性** 以及 **系統可觀測性** 等核心難題。

系統能自動從多元金融來源抓取實時數據，並透過非同步管線進行校驗與落地，最後提供視覺化的監控面板。

##  系統架構圖 (Pipeline Architecture)
本系統採用生產者-消費者模型，確保組件間的高度解耦：

```mermaid
graph TD
    A[FastAPI Producer] -->|Task Dispatch| B(Redis Queue)
    B -->|Task Consumption| C[Celery Worker Cluster]
    C -->|Dynamic Scrape| D[Playwright / HTTPX]
    D -->|Data Validation| E[Pydantic Models]
    E -->|Time-series Load| F[(ClickHouse)]
    E -->|Meta Data| G[(PostgreSQL)]
    H[Prometheus] -->|Scrape Metrics| A
    I[Grafana] -->|Visualize| H
