# backend/app/services/seeder.py
"""Automated demo clinical data seeder for portfolio & RAG evaluation.

Pre-populates the database and vector store with high-fidelity simulated patient clinical records
so recruiters and evaluators can immediately experience accurate semantic retrieval and medical citations.
"""

import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

from ..domain.models.user import User
from ..domain.models.document import Document, IngestionTask, DocumentChunk
from ..services.chunking import chunk_text
from ..services.embeddings import embed_texts
from ..infrastructure.qdrant import get_qdrant_client

logger = logging.getLogger(__name__)

COLLECTION_NAME = "documents"
VECTOR_SIZE = 384  # Matches sentence-transformers all-MiniLM-L6-v2

DEMO_DOCUMENTS = [
    {
        "filename": "Cardiology_Discharge_Summary_PT_01.txt",
        "content_type": "text/plain",
        "text": """PATIENT: John Doe (58M) | MRN: #49201-CD | ADMISSION DATE: 2026-07-28 | DISCHARGE DATE: 2026-08-01

CHIEF COMPLAINT:
Severe crushing substernal chest pain radiating to the left arm and jaw associated with acute diaphoresis.

HISTORY OF PRESENT ILLNESS (HPI):
58-year-old male with known baseline chronic hypertension and hyperlipidemia presented to the emergency department with acute onset of crushing substernal chest discomfort while exercising. Electrocardiogram (ECG) demonstrated acute ST-segment elevations in anteroseptal leads V1-V4. Patient underwent emergent coronary angiography and heart catheterization, which revealed severe 95% stenosis of the mid-Left Anterior Descending (LAD) artery. Two drug-eluting stents (DES) were placed successfully with successful restoration of normal TIMI 3 distal flow.

ASSESSMENT:
1. Acute Anteroseptal Myocardial Infarction (STEMI) successfully treated with LAD stent angioplasty.
2. Controlled chronic hypertension.
3. Dyslipidemia, elevated LDL baseline at 168 mg/dL.

PLAN:
1. Initiate dual antiplatelet therapy: Aspirin 81 mg by mouth daily indefinitely, plus Clopidogrel 75 mg by mouth daily for a minimum duration of 12 uninterrupted months to prevent localized intrastent thrombosis.
2. Atorvastatin 80 mg by mouth once daily at bedtime for aggressive atherosclerotic plaque stabilization.
3. Metoprolol Tartrate 25 mg by mouth twice daily for cardiac myocardial oxygen demand optimization.
4. Follow-up consultation scheduled in cardiology clinic with Dr. Sarah Vance in 14 days.
5. Activity restrictions: Avoid lifting greater than 10 pounds or intense exertion for at least 7 days post-discharge."""
    },
    {
        "filename": "Neurology_Consultation_PT_02.txt",
        "content_type": "text/plain",
        "text": """PATIENT: Elena Rostova (42F) | MRN: #88392-NR | CONSULTATION DATE: 2026-07-30 | CLINICAL SPECIALTY: Neurology

CHIEF COMPLAINT:
Intermittent progressive visual blurring in the right eye associated with retro-orbital pain upon ocular movement, accompanied by ascending tingling numbness in the right upper hand and fingertips over the past 5 days.

ASSESSMENT & DIAGNOSTIC FINDINGS:
Ophthalmic fundoscopic evaluation demonstrated subtle right optic disk blurring indicative of active unilateral retrobulbar optic neuritis. Neurological examination identified hyperreflexia in both lower extremities (3+) and positive Hoffmann sign on the right.
Brain Magnetic Resonance Imaging (MRI) with and without intravenous gadolinium contrast demonstrated multiple well-demarcated T2/FLAIR hyperintense demyelinating periventricular, juxtacortical, and infratentorial white matter lesions. Two lesions within the corpus callosum demonstrated active gadolinium enhancement, confirming synchronized blood-brain barrier breakdown and acute clinical inflammatory demyelination.
Lumbar puncture cerebrospinal fluid (CSF) analysis revealed elevated IgG synthesis rate and strongly positive oligoclonal bands (>8 specific immunoglobulin gamma bands present in CSF that were entirely absent in corresponding serum sample).

DIAGNOSIS:
Relapsing-Remitting Multiple Sclerosis (RRMS) with active acute demyelinating CNS relapse manifesting as right optic neuritis and localized extremity paresthesis.

PLAN:
1. Administer acute intravenous immunosuppressive pulse therapy: Methylprednisolone 1000 mg infusion daily for 5 consecutive days to suppress active focal inflammatory demyelination.
2. Initiate high-efficacy disease-modifying therapy (DMT): Ocrelizumab 300 mg intravenous infusion as initial dose, followed by second 300 mg dose exactly 14 days later; thereafter transition to maintenance schedule of 600 mg intravenous infusion once every 6 months.
3. Comprehensive physical therapy and rehabilitative medicine referral to preserve vestibular balance, endurance, and fine motor coordinate dexterity.
4. Follow-up Brain and Cervical Spine MRI scan scheduled in 4 months to evaluate therapeutic plaque stabilization and absence of emerging gadolinium-enhancing lesions."""
    },
    {
        "filename": "Oncology_Care_Plan_PT_03.txt",
        "content_type": "text/plain",
        "text": """PATIENT: Marcus Vance (65M) | MRN: #11094-ON | ONCOLOGY REVIEW DATE: 2026-08-02 | ATTENDING: Dr. Aris Thorne

CLINICAL HISTORY & DIAGNOSIS:
65-year-old male former cigarette smoker presented with chronic unremitting non-productive cough, progressive exertional shortness of breath, and an unintentional 15-pound solid body mass loss over 12 weeks.
Computed Tomography (CT) scan of chest revealed a 3.5 cm dense spiculated mass centered within the Right Upper Lobe (RUL), adjacent to mediastinal lymph nodes. Subsequent diagnostic bronchoscopy and Endobronchial Ultrasound-Guided Transbronchial Needle Aspiration (EBUS-TBNA) confirmed malignant primary lung pathology.
Histological diagnostic criteria: Stage IIIA (T2a N2 M0) Primary Pulmonary Adenocarcinoma.
Molecular biomarker diagnostic screening profile: Positive for targeted epidermal growth factor receptor (EGFR) exon 19 deletion mutation; negative for ALK rearrangement, ROS1 translocation, and KRAS oncogene alterations. Programmed death-ligand 1 (PD-L1) tumor proportion score expression evaluated at less than 1%.

TREATMENT PLAN:
1. Patient reviewed at Multidisciplinary Tumor Board; determined candidate for targeted molecular induction therapy given confirmed positive EGFR exon 19 deletion mutation status.
2. Initiate oral Tyrosine Kinase Inhibitor (TKI) regimen: Osimertinib 80 mg administered orally once daily without interruptions.
3. Clinical surveillance criteria: Complete blood counts, renal function panels, and comprehensive hepatic serum enzyme screening (AST, ALT, Bilirubin) ordered monthly while on active Osimertinib therapy to monitor for hepatotoxicity or cytopenias.
4. Baseline transthoracic echocardiogram ordered to evaluate Left Ventricular Ejection Fraction (LVEF) prior to continuous TKI exposure.
5. Follow-up restaging baseline torso fluorodeoxyglucose (FDG) PET-CT imaging scheduled in 8 weeks to quantify primary RUL metabolic attenuation and tumor volume regression prior to surgical lobectomy consultation."""
    }
]


def seed_demo_clinical_data(db: Session) -> None:
    """Check if demo documents exist; if empty, seed simulated clinical records into database and vector store."""
    existing_doc = db.query(Document).filter(Document.filename == DEMO_DOCUMENTS[0]["filename"]).first()
    if existing_doc:
        if db.query(DocumentChunk).filter(DocumentChunk.document_id == existing_doc.id).count() > 0:
            logger.info("Demo clinical dataset already present with valid chunks; skipping seeding.")
            return
        else:
            logger.info("Incomplete demo seeding detected; wiping incomplete records for clean re-seed...")
            for d_data in DEMO_DOCUMENTS:
                db.query(Document).filter(Document.filename == d_data["filename"]).delete()
            db.commit()

    logger.info("Seeding demo clinical dataset for RAG evaluation...")
    
    from ..core.deps import _get_or_create_demo_user
    author = _get_or_create_demo_user(db)
    author_id = author.id if author else None

    qdrant_available = False
    try:
        qclient = get_qdrant_client()
        try:
            qclient.get_collection(COLLECTION_NAME)
        except (UnexpectedResponse, Exception):
            qclient.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
        qdrant_available = True
    except Exception as e:
        logger.warning(f"Qdrant vector store initialization warning ({e}). Continuing database seeding.")

    for doc_data in DEMO_DOCUMENTS:
        text_content = doc_data["text"]

        document = Document(
            filename=doc_data["filename"],
            content_type=doc_data["content_type"],
            path=f"demo_seed/{doc_data['filename']}",
            uploaded_by=author_id,
        )
        db.add(document)
        db.flush()

        task = IngestionTask(
            id=str(uuid.uuid4()),
            document_id=document.id,
            status="completed",
        )
        db.add(task)
        db.flush()

        raw_chunks = chunk_text(text_content)
        if not raw_chunks:
            continue

        chunk_texts = [content for content, _ in raw_chunks]
        try:
            embeddings = embed_texts(chunk_texts)
        except Exception as e:
            logger.warning(f"Could not compute semantic embeddings during seed ({e}). Using dummy zero embeddings.")
            embeddings = [[0.0] * VECTOR_SIZE for _ in chunk_texts]

        points_to_upsert = []
        for chunk_idx, ((content, section_title), embedding) in enumerate(zip(raw_chunks, embeddings)):
            qdrant_uuid = str(uuid.uuid4())
            db_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk_idx,
                content=content,
                section_title=section_title,
                embedding_id=qdrant_uuid,
            )
            db.add(db_chunk)

            if qdrant_available:
                points_to_upsert.append(
                    PointStruct(
                        id=qdrant_uuid,
                        vector=embedding,
                        payload={
                            "document_id": str(document.id),
                            "chunk_id": str(db_chunk.id or chunk_idx),
                            "filename": doc_data["filename"],
                            "content": content,
                            "section_title": section_title or "General Section",
                            "chunk_index": chunk_idx,
                        },
                    )
                )

        if qdrant_available and points_to_upsert:
            try:
                qclient.upsert(collection_name=COLLECTION_NAME, points=points_to_upsert)
            except Exception as err:
                logger.warning(f"Failed to upsert demo vectors to Qdrant: {err}")

    db.commit()
    logger.info(f"Successfully seeded {len(DEMO_DOCUMENTS)} clinical documents into database!")
