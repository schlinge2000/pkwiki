---
title: Argo Workflows — Inferenz-SaaS-Architektur
type: concept
domain: tech
sources: [raw/docs/Report Demand AI Architecture.docx]
related: ["[[foundation-models]]", "[[prognose-as-a-service]]", "[[demand-ai]]"]
confidence: high
last_updated: 2026-04-17
---

# Argo Workflows — Inferenz-SaaS-Architektur

Technische Architekturentscheidung für die Demand AI Inferenz-Plattform: Ablösung von AWS-nativen Services (Lambda, Step Functions, EventBridge) durch Argo Workflows auf Kubernetes.

## Ausgangslage

Bestehende Architektur mit statisch definierten Abläufen stieß an Grenzen bei:
- In-Sample Evaluationen ohne erneuten Daten-Upload
- Dynamischen, kontextabhängigen Task-Abfolgen
- Skalierung über viele Mandanten

## Architekturentscheidung: Argo Workflows

**Gründe für Argo Workflows:**
- Deklarative Orchestrierung (Kubernetes-native YAML)
- Containerisierte Tasks — vollständig modular und erweiterbar
- Flexible Reihenfolgen und Abhängigkeiten ohne Architekturanpassung
- Versionierbar und automatisierbar

## Asset-Paradigma

Alle verarbeiteten Objekte werden als **Assets** verstanden:
- Input-Daten
- Modelldateien
- Evaluationsmetriken
- Forecast-Artefakte

Assets können frei kombiniert und von funktionalen Bausteinen konsumiert oder produziert werden → einheitliches Paradigma für Inferenz, Training, Evaluation und Model-Management.

## Baukastenprinzip

Kunde/Applikation kann selbst festlegen:
- Welche Tasks für ein Planungsobjekt ausgeführt werden
- In welcher Reihenfolge
- Welche Ein-/Ausgabedaten als Grundlage dienen

Steuerung über YAML/Spec-Files → transparent, reproduzierbar, versionierbar.

## Ausblick: LLM-gesteuerte Workflows

> "Berechne optimale Wiederbeschaffungszeit für alle Artikel mit Servicegrad >95%"

Ein LLM könnte Spec-Files automatisch generieren aus natürlichsprachlichen Anforderungen — analog zu agentischen Workflows (OpenAI). Visualisierung der Abläufe über UI.

## Strategische Bedeutung

Die Architektur wird zur universellen Rechen- und Entscheidungsumgebung für Supply-Chain-Software:
- Wiederbeschaffungszeiten
- Quantilsanalysen
- Losgrößenoptimierungen
- Heuristische Dispositionslogiken

Alle folgen demselben Muster: **Planungsobjekt + Daten + Task**.
