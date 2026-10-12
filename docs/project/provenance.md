# Эх сурвалж, хувилбар ба ажлын гарал

## Оролтын баримт

Хэрэглэгч эхний зургаан семинарын handout, өөрийн W01–W03 Word тайлан, W04–W05 PDF, W05 YAML, өмнөх W06 тайланг өгсөн. Файлын нэр, хэмжээ, SHA-256 нь [manifest](../../sources/manifest.json)-д бий. Давхардлыг hash-аар танина.

Handout нь даалгаврын шалгуур; оюутны тайлан нь өмнөх ажлын мэдэгдэл; source/test/log нь шалгах нотолгоо. Interview, peer review, hosted URL, model transcript, code execution-ийг нөхөж зохиохгүй.

## Хувилбарын үндэс

Одоогийн шаардлагын редакцийн суурь `Week_03_FoodFlow.docx`. Хуучин PHTBB-3.pdf-ээс FR-06/07, FR-10/11, FR-13, NFR-01 өөр. [SRS](../requirements/srs.md), [CHANGELOG](../../CHANGELOG.md)-д тэмдэглэсэн. “Суурь” нь энэ баримтжуулалтын нэг мөр редакц; албан ёсны team approval биш.

ADR-ууд Proposed. Persistence/idempotency consistency-ийн нэмэлт тайлбар санал болгосон сайжруулалт. W05 contract нь хэрэглэгчийн YAML-ээс уламжилсан, local mock тусдаа хязгаартай. W06 class нь PDF-ээс сэргээн байгуулсан teaching module.

## AI ашиглалт

Найруулга, бүтэц, код, шалгалтыг Codex туслан бэлтгэсэн. Номын бүрэн эх, human independent baseline, GPT-4/Claude raw output ирээгүй. Negative fixture нь зориудын алдаа; model-ийн санамсаргүй hallucination-ийн нотолгоо биш. [W06 provenance](../../review/provenance.md) дэлгэрэнгүй.

AI ажил бүрт model/date/prompt/input hash/raw output/diff/verifier/reference-ийг [загвараар](../../templates/ai-audit.md) бүртгэнэ. Бодит review хийгдээгүй үед хүний нэр/гарын үсэг/approval date бөглөхгүй.

## Эшлэлийн зарчим

Номын chapter/page холбоог handout-аар дамжуулсан бол тэгж тэмдэглэнэ. Шалгаагүй үгчилсэн эшлэл зохиохгүй. Technical claim-д primary official documentation холбоно. Web/UI туршаагүй дүгнэлтийг conceptual assessment гэж тэмдэглэнэ.
