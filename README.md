Run this script in the server directory to build
gcloud builds submit --tag gcr.io/sleeping-aid-295720/sleeping-aid

Deploy using
gcloud run deploy --region us-central1 --platform managed --image gcr.io/sleeping-aid-295720/sleeping-aid

In node_modules>.bin> run firebase deploy with --only hosting because the container has already been deployed
firebase deploy --only hosting

    or run firebase serve to spin up on localhost


https://sleeping-aid-xolr33b7eq-uc.a.run.app