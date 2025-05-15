#!/bin/bash

# Script to create the initial directory structure for the thesis
echo "Creating thesis directory structure..."

# Create base directories
mkdir -p pages
mkdir -p build/tex
mkdir -p build/pdf
mkdir -p build/logs
mkdir -p schema

# Create directories for the pages
for i in {1..5}; do
  mkdir -p "pages/$i"
  echo "Created directory for page $i"
done

# Create the JSON schema file
echo "Creating JSON schema file..."
cat > schema/page_schema.json << 'EOF'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Thesis Page Schema",
  "description": "Schema for a thesis page content",
  "type": "object",
  "required": ["title", "pageNumber"],
  "properties": {
    "title": {
      "type": "string",
      "description": "The title of the page/chapter/section"
    },
    "pageNumber": {
      "type": "integer",
      "description": "The page number"
    },
    "sectionLevel": {
      "type": "integer",
      "description": "Level of the section (1=chapter, 2=section, 3=subsection, etc.)",
      "minimum": 1,
      "maximum": 5,
      "default": 1
    },
    "content": {
      "type": "array",
      "description": "Content blocks for this page",
      "items": {
        "type": "object",
        "required": ["type", "data"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["text", "image", "table", "code", "equation", "listing"],
            "description": "Type of content block"
          },
          "data": {
            "type": "object",
            "description": "Content block data, depends on type"
          }
        },
        "allOf": [
          {
            "if": {
              "properties": { "type": { "const": "text" } }
            },
            "then": {
              "properties": {
                "data": {
                  "oneOf": [
                    {
                      "required": ["text"],
                      "properties": {
                        "text": {
                          "type": "string",
                          "description": "Inline text content"
                        }
                      }
                    },
                    {
                      "required": ["textPath"],
                      "properties": {
                        "textPath": {
                          "type": "string",
                          "description": "Path to external text file"
                        }
                      }
                    }
                  ]
                }
              }
            }
          },
          {
            "if": {
              "properties": { "type": { "const": "image" } }
            },
            "then": {
              "properties": {
                "data": {
                  "required": ["imagePath"],
                  "properties": {
                    "imagePath": {
                      "type": "string",
                      "description": "Path to image file"
                    },
                    "caption": {
                      "type": "string",
                      "description": "Image caption"
                    },
                    "label": {
                      "type": "string",
                      "description": "Reference label for the image"
                    }
                  }
                }
              }
            }
          },
          {
            "if": {
              "properties": { "type": { "const": "table" } }
            },
            "then": {
              "properties": {
                "data": {
                  "required": ["tableData"],
                  "properties": {
                    "tableData": {
                      "type": "array",
                      "description": "Table data as a 2D array",
                      "items": {
                        "type": "array",
                        "items": {
                          "type": "string"
                        }
                      }
                    },
                    "caption": {
                      "type": "string",
                      "description": "Table caption"
                    },
                    "label": {
                      "type": "string",
                      "description": "Reference label for the table"
                    }
                  }
                }
              }
            }
          },
          {
            "if": {
              "properties": { "type": { "const": "code" } }
            },
            "then": {
              "properties": {
                "data": {
                  "required": ["code"],
                  "properties": {
                    "code": {
                      "type": "string",
                      "description": "Code content"
                    },
                    "language": {
                      "type": "string",
                      "description": "Programming language",
                      "default": "text"
                    },
                    "caption": {
                      "type": "string",
                      "description": "Code caption"
                    },
                    "label": {
                      "type": "string",
                      "description": "Reference label for the code"
                    }
                  }
                }
              }
            }
          },
          {
            "if": {
              "properties": { "type": { "const": "equation" } }
            },
            "then": {
              "properties": {
                "data": {
                  "required": ["equation"],
                  "properties": {
                    "equation": {
                      "type": "string",
                      "description": "LaTeX equation content"
                    },
                    "label": {
                      "type": "string",
                      "description": "Reference label for the equation"
                    }
                  }
                }
              }
            }
          },
          {
            "if": {
              "properties": { "type": { "const": "listing" } }
            },
            "then": {
              "properties": {
                "data": {
                  "required": ["code"],
                  "properties": {
                    "code": {
                      "type": "string",
                      "description": "Code content"
                    },
                    "language": {
                      "type": "string",
                      "description": "Programming language",
                      "default": "text"
                    },
                    "caption": {
                      "type": "string",
                      "description": "Listing caption"
                    },
                    "label": {
                      "type": "string",
                      "description": "Reference label for the listing"
                    }
                  }
                }
              }
            }
          }
        ]
      }
    },
    "references": {
      "type": "array",
      "description": "References used in this page",
      "items": {
        "type": "object",
        "required": ["id", "citation"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Reference identifier"
          },
          "citation": {
            "type": "string",
            "description": "BibTeX citation"
          }
        }
      }
    }
  }
}
EOF

echo "Directory structure and JSON schema created successfully."