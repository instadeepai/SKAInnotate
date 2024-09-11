# SKAInnotate
<img src="https://github.com/instadeepai/SKAInnotate/assets/18593619/5b7f895f-9479-4d1c-82d0-5bd2cd744bf7" align="right"
     alt="SKAInnotate logo" width="120" height="120">
     
SKAInnotate is a data annotation tool designed for Google SKAI and operates within Google Colab Notebooks. It consists of two main notebooks: one for project administration and another for annotators.

## Project Admin Notebook (`Admin-Notebook.ipynb`)

The Project Admin notebook provides the following capabilities:

1. **Create Annotation Projects**: Set up new annotation projects.
2. **Manage Annotators**: Add or remove annotators from projects.
3. **Configure Project Settings**: Define project titles, storage buckets, maximum annotators per task, and other configurations.
4. **Assign Tasks**: Assign annotation tasks to annotators.
5. **View and Export Annotations**: Access and export annotations from all annotators.

## Setup

### Prerequisites

To use SKAInnotate effectively, ensure the following prerequisites are met:

- **Google Cloud Project Permissions**: Configure the Google Cloud project with permissions to manage users and resources.
The following roles should be sufficient for the admin; Cloud SQL Admin, Storage Admin and roles/resourcemanager.projectIamAdmin.
- **Data Upload**: All data to be labeled must be uploaded to a Google Cloud Storage bucket.

### Adding Data for Labeling

To add data for labeling, follow these steps:

1. Place a metadata CSV file in the same path as the data.
2. The CSV file must include the following columns:
   - `example_id`: Unique ID for each example.
   - `image`: Unique filename for each example.

### Global Configurations

Configure the following global settings for your SKAInnotate project:

- `project_id`: Google Cloud Platform (GCP) project ID.
- `region`: Location of the GCP project.
- `instance_name`: Name of the Google Cloud SQL instance.
- `root_password`: Password for the PostgreSQL database user.

### Project Configurations

Define project-specific settings:

- `project_title`: Title of the project.
- `bucket_name`: Name of the Google Cloud Storage bucket.
- `bucket_prefix`: Prefix for the bucket (e.g., `my-storage/inner-storage` for data path `gs://my-bucket/my-storage/inner-storage/image1.png`).
- `comma_separated_labels`: Labels stored in the database as a string. Include `"skip"` to allow annotators to skip uncertain labels.
- `max_annotators_per_example`: Maximum number of annotators per task to provide different perspectives.
- `completion_deadline`: Deadline to complete annotation tasks.

## Annotator Notebook (`Annotator-Notebook.ipynb`)

The Annotator notebook is used by annotators to perform the following tasks:

1. **Receive Assigned Tasks**: Retrieve tasks assigned by the project admin.
2. **Label Tasks**: Annotate data using a user interface.
3. **Write Annotations**: Store annotations securely in a central cloud database.

### Setup

Annotators need to set up the following configurations:

- `project_id`: GCP project ID.
- `region`: GCP project location.
- `instance_name`: Google Cloud SQL instance name.
- **Authentication**: Annotators require a username and password provided by the project admin to access assigned tasks.
